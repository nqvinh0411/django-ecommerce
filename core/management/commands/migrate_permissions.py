"""
Django management command để migrate permissions từ app-specific sang core permissions
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import re
import glob
from pathlib import Path


class Command(BaseCommand):
    help = 'Migrate app-specific permissions to core permissions system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Specific app to migrate (if not provided, migrates all apps)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if duplicates detected',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🔧 Starting Permission Migration Process...')
        )
        
        # Define mapping của duplicate permissions
        self.permission_mapping = {
            'IsAdminOrReadOnly': 'core.permissions',
            'IsOwnerOrAdmin': 'core.permissions',
            'IsOwnerOrReadOnly': 'core.permissions',
            'IsAdminUser': 'rest_framework.permissions',  # Django built-in
            'IsAuthenticated': 'rest_framework.permissions',  # Django built-in
        }
        
        # Core permissions available
        self.core_permissions = [
            'IsAdminUser',
            'IsAdminOrReadOnly', 
            'IsOwner',
            'IsOwnerOrReadOnly',
            'IsOwnerOrAdmin',
            'IsSellerOrAdmin',
            'CreateOnlyPermission'
        ]
        
        if options['app']:
            self.migrate_single_app(options['app'])
        else:
            self.migrate_all_apps()
            
        self.stdout.write(
            self.style.SUCCESS('✅ Permission migration completed!')
        )

    def migrate_all_apps(self):
        """Migrate tất cả apps trong project"""
        base_dir = Path(settings.BASE_DIR)
        
        # Tìm tất cả Django apps (có __init__.py và models.py hoặc views.py)
        for app_path in base_dir.iterdir():
            if (app_path.is_dir() and 
                (app_path / '__init__.py').exists() and
                app_path.name not in ['core', 'venv', '__pycache__', '.git']):
                
                self.migrate_single_app(app_path.name)

    def migrate_single_app(self, app_name):
        """Migrate permissions cho một app cụ thể"""
        self.stdout.write(f"\n📁 Processing app: {app_name}")
        
        app_path = Path(settings.BASE_DIR) / app_name
        if not app_path.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ App {app_name} not found")
            )
            return
            
        # 1. Analyze app permissions
        permissions_file = app_path / 'permissions.py'
        duplicates = self.analyze_permissions(permissions_file) if permissions_file.exists() else []
        
        # 2. Update imports in views/viewsets
        view_files = list(app_path.glob('**/views*.py')) + list(app_path.glob('**/viewsets*.py'))
        for view_file in view_files:
            self.update_imports(view_file, app_name)
            
        # 3. Remove duplicate permissions
        if duplicates and permissions_file.exists():
            self.clean_permissions_file(permissions_file, duplicates)

    def analyze_permissions(self, permissions_file):
        """Analyze permissions file để tìm duplicates"""
        if not permissions_file.exists():
            return []
            
        duplicates = []
        
        try:
            with open(permissions_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Tìm class definitions
            class_pattern = r'class\s+(\w+)\s*\([^)]*permissions\.BasePermission[^)]*\):'
            matches = re.findall(class_pattern, content)
            
            for class_name in matches:
                if class_name in self.permission_mapping:
                    duplicates.append(class_name)
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Found duplicate: {class_name}")
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error analyzing {permissions_file}: {e}")
            )
            
        return duplicates

    def update_imports(self, file_path, app_name):
        """Update imports trong view/viewset files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Pattern 1: from .permissions import IsOwnerOrAdmin
            pattern1 = r'from \.permissions import ([^,\n]+(?:,\s*[^,\n]+)*)'
            
            def replace_local_imports(match):
                imports = match.group(1)
                import_list = [imp.strip() for imp in imports.split(',')]
                
                core_imports = []
                local_imports = []
                
                for imp in import_list:
                    if imp in self.core_permissions:
                        core_imports.append(imp)
                    else:
                        local_imports.append(imp)
                
                result = ""
                if core_imports:
                    result += f"from core.permissions import {', '.join(core_imports)}\n"
                if local_imports:
                    result += f"from .permissions import {', '.join(local_imports)}"
                    
                return result.rstrip()
            
            content = re.sub(pattern1, replace_local_imports, content)
            
            # Pattern 2: from core.permissions.base import IsAdminOrReadOnly
            pattern2 = r'from core\.permissions\.base import'
            replacement2 = 'from core.permissions import'
            content = re.sub(pattern2, replacement2, content)
            
            # Write changes nếu có
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.stdout.write(f"  ✅ Updated imports: {file_path.name}")
                else:
                    self.stdout.write(f"  🔍 Would update: {file_path.name}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating {file_path}: {e}")
            )

    def clean_permissions_file(self, permissions_file, duplicates):
        """Remove duplicate permission classes"""
        try:
            with open(permissions_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Remove duplicate classes
            for duplicate in duplicates:
                # Pattern để match toàn bộ class definition
                pattern = rf'class\s+{duplicate}\s*\([^)]*\):.*?(?=class\s+\w+|$)'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
                
            # Clean up multiple empty lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = content.strip()
            
            if content != original_content:
                if not self.dry_run:
                    if content.strip():
                        # File còn content, write lại
                        with open(permissions_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.stdout.write(f"  ✅ Cleaned: {permissions_file.name}")
                    else:
                        # File empty, có thể xóa
                        if self.force:
                            permissions_file.unlink()
                            self.stdout.write(f"  🗑️  Removed empty: {permissions_file.name}")
                        else:
                            self.stdout.write(f"  ⚠️  File would be empty: {permissions_file.name} (use --force to remove)")
                else:
                    self.stdout.write(f"  🔍 Would clean: {permissions_file.name}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error cleaning {permissions_file}: {e}")
            )

    def show_summary(self):
        """Show migration summary"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 MIGRATION SUMMARY")
        self.stdout.write("="*50)
        
        # Apps that need attention
        self.stdout.write("\n🔄 Apps migrated:")
        # Implementation would track and show actual results
        
        self.stdout.write("\n📚 Next steps:")
        self.stdout.write("1. Run tests to ensure no regressions")
        self.stdout.write("2. Update documentation")
        self.stdout.write("3. Review remaining custom permissions") 