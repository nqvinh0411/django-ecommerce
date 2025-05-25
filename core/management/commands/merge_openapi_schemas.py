"""
Management command để gộp tất cả các OpenAPI schemas thành một schema chính.

Command này sẽ quét tất cả các file OpenAPI schema riêng lẻ của từng module
và gộp chúng thành một schema chính duy nhất.
"""
import os
import yaml
import copy
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Gộp tất cả các OpenAPI schemas thành một schema chính'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file',
            type=str,
            default=os.path.join(str(settings.BASE_DIR), 'docs', 'api', 'openapi', 'e_commerce_api.yaml'),
            help='Đường dẫn đến file schema chính'
        )
        
        parser.add_argument(
            '--schemas-dir',
            type=str,
            default=os.path.join(str(settings.BASE_DIR), 'docs', 'api'),
            help='Thư mục chứa các schemas riêng lẻ'
        )

    def handle(self, *args, **options):
        output_file = options['output_file']
        schemas_dir = options['schemas_dir']
        
        # Tạo schema chính ban đầu
        main_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "E-commerce API",
                "version": "1.0.0",
                "description": "API chính cho hệ thống E-commerce"
            },
            "servers": [
                {
                    "url": "/api/v1",
                    "description": "API chính của E-commerce"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "responses": {
                    "BadRequest": {
                        "description": "Dữ liệu không hợp lệ",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 400},
                                        "message": {"type": "string", "example": "Dữ liệu không hợp lệ"},
                                        "errors": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "Unauthorized": {
                        "description": "Không có quyền truy cập",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 401},
                                        "message": {"type": "string", "example": "Không có quyền truy cập"}
                                    }
                                }
                            }
                        }
                    },
                    "Forbidden": {
                        "description": "Không được phép truy cập",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 403},
                                        "message": {"type": "string", "example": "Không được phép truy cập"}
                                    }
                                }
                            }
                        }
                    },
                    "NotFound": {
                        "description": "Không tìm thấy tài nguyên",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "error"},
                                        "status_code": {"type": "integer", "example": 404},
                                        "message": {"type": "string", "example": "Không tìm thấy tài nguyên"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Quét tất cả các module để tìm file schema
        module_schemas = []
        
        for module_dir in os.listdir(schemas_dir):
            module_openapi_dir = os.path.join(schemas_dir, module_dir, 'openapi')
            if os.path.isdir(module_openapi_dir):
                for file_name in os.listdir(module_openapi_dir):
                    if file_name.endswith('.yaml') or file_name.endswith('.yml'):
                        schema_file = os.path.join(module_openapi_dir, file_name)
                        try:
                            with open(schema_file, 'r', encoding='utf-8') as f:
                                schema = yaml.safe_load(f)
                                module_schemas.append({
                                    'name': module_dir,
                                    'schema': schema
                                })
                                self.stdout.write(f"Đã đọc schema từ {schema_file}")
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Lỗi khi đọc schema từ {schema_file}: {str(e)}"))
        
        # Gộp các schemas
        for module_schema in module_schemas:
            module_name = module_schema['name']
            schema = module_schema['schema']
            
            # Gộp paths
            if 'paths' in schema:
                for path, path_item in schema['paths'].items():
                    # Chuẩn hóa đường dẫn API với tiền tố module
                    normalized_path = f"/{module_name}{path}" if not path.startswith(f"/{module_name}") else path
                    main_schema['paths'][normalized_path] = copy.deepcopy(path_item)
            
            # Gộp schemas
            if 'components' in schema and 'schemas' in schema['components']:
                for schema_name, schema_obj in schema['components']['schemas'].items():
                    # Thêm tiền tố module vào tên schema để tránh xung đột
                    prefixed_schema_name = f"{module_name.title()}{schema_name}"
                    main_schema['components']['schemas'][prefixed_schema_name] = copy.deepcopy(schema_obj)
            
            # Thêm tags
            if 'tags' in schema:
                if 'tags' not in main_schema:
                    main_schema['tags'] = []
                
                for tag in schema['tags']:
                    # Kiểm tra nếu tag đã tồn tại
                    existing_tag = next((t for t in main_schema['tags'] if t['name'] == tag['name']), None)
                    if not existing_tag:
                        main_schema['tags'].append(copy.deepcopy(tag))
        
        # Ghi file schema chính
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(main_schema, f, sort_keys=False, default_flow_style=False)
        
        self.stdout.write(self.style.SUCCESS(f"Đã gộp các schemas thành công và lưu vào {output_file}"))
