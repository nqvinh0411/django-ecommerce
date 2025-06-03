# 🔐 Permission Usage Guide - E-Commerce Django

## 📋 Tổng quan

Guide này hướng dẫn developers về cách sử dụng permission system trong e-commerce Django project. Chúng ta có **centralized permission system** trong `core.permissions` để đảm bảo consistency và reusability.

## 🎯 **Core Principles**

### ✅ **DO**
```python
# ✅ Sử dụng core permissions
from core.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly

# ✅ Combine với Django built-in permissions  
from rest_framework import permissions
permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

# ✅ Use descriptive permission classes
permission_classes = [IsSellerOrAdmin]  # Clear intent
```

### ❌ **DON'T**
```python
# ❌ Không tự define duplicate permissions
class IsOwnerOrAdmin(permissions.BasePermission):  # Duplicate!
    # Logic đã có trong core.permissions
    
# ❌ Không import từ .base
from core.permissions.base import IsAdminOrReadOnly  # WRONG!

# ❌ Không mix import styles
from core.permissions import IsOwnerOrAdmin
from core.permissions.base import IsAdminOrReadOnly  # Inconsistent!
```

## 🏗️ **Available Core Permissions**

### **1. Admin Permissions**
```python
from core.permissions import IsAdminUser, IsAdminOrReadOnly

# IsAdminUser - Chỉ admin mới có access
permission_classes = [IsAdminUser]

# IsAdminOrReadOnly - Admin có full access, others read-only
permission_classes = [IsAdminOrReadOnly]
```

### **2. Owner-based Permissions**
```python
from core.permissions import IsOwner, IsOwnerOrReadOnly, IsOwnerOrAdmin

# IsOwner - Chỉ owner có access
permission_classes = [IsOwner]

# IsOwnerOrReadOnly - Owner có full access, others read-only  
permission_classes = [IsOwnerOrReadOnly]

# IsOwnerOrAdmin - Owner hoặc admin có access
permission_classes = [IsOwnerOrAdmin]
```

### **3. Role-based Permissions**
```python
from core.permissions import IsSellerOrAdmin

# IsSellerOrAdmin - Sellers hoặc admin có access
permission_classes = [IsSellerOrAdmin]
```

### **4. Special Permissions**
```python
from core.permissions import CreateOnlyPermission, AllowAny, IsAuthenticated

# CreateOnlyPermission - Chỉ cho phép POST requests
permission_classes = [CreateOnlyPermission]
```

## 📚 **Usage Patterns by App Type**

### **🛒 E-commerce Apps (products, orders, cart)**
```python
# Products - Public read, seller/admin write
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {
        'list': [permissions.AllowAny],
        'retrieve': [permissions.AllowAny], 
        'create': [IsSellerOrAdmin],
        'update': [IsOwnerOrAdmin],  # Product owner or admin
        'destroy': [IsAdminOrReadOnly]
    }

# Orders - Customer owns their orders
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
```

### **👥 User Management Apps (users, customers)**
```python
# Users - Admin manages all, users manage self
class UserAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

class UserSelfViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
```

### **📊 Admin/Management Apps (reports, settings)**
```python
# Admin-only apps
class ReportsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

# Public read, admin write
class SettingsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
```

### **🎫 Support Apps (tickets, help)**
```python
# Users see own tickets, admin sees all
class SupportTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
```

## 🔧 **Advanced Usage with PermissionByActionMixin**

```python
from core.mixins.views import PermissionByActionMixin
from core.permissions import IsOwnerOrAdmin, IsSellerOrAdmin

class ProductViewSet(PermissionByActionMixin, viewsets.ModelViewSet):
    # Default permissions
    permission_classes = [permissions.IsAuthenticated]
    
    # Action-specific permissions
    permission_classes_by_action = {
        'list': [permissions.AllowAny],
        'retrieve': [permissions.AllowAny],
        'create': [permissions.IsAuthenticated, IsSellerOrAdmin],
        'update': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'destroy': [permissions.IsAdminUser],
        'bulk_update': [permissions.IsAdminUser],
        'analytics': [IsSellerOrAdmin],
    }
```

## 🧪 **Permission Testing**

### **Unit Tests**
```python
from django.test import TestCase
from core.permissions import IsOwnerOrAdmin

class TestPermissions(TestCase):
    def test_owner_access(self):
        """Test that owner có access"""
        permission = IsOwnerOrAdmin()
        # Create test user, object, request
        # Assert permission.has_object_permission() == True
        
    def test_admin_access(self):
        """Test that admin có access"""
        # Similar test logic
```

### **Integration Tests**
```python
from rest_framework.test import APITestCase

class ProductAPITestCase(APITestCase):
    def test_seller_can_create_product(self):
        """Test seller có thể tạo product"""
        # Create seller user
        # POST to /api/v1/products/
        # Assert 201 Created
        
    def test_customer_cannot_create_product(self):
        """Test customer không thể tạo product"""
        # Create customer user  
        # POST to /api/v1/products/
        # Assert 403 Forbidden
```

## 🏭 **When to Create Custom Permissions**

### **✅ Create Custom When:**
- **Domain-specific logic**: `IsCustomerOwner` for customer addresses
- **Complex business rules**: `CanManagePromotions` with specific conditions
- **Multi-field ownership**: Permission checking multiple related objects

### **❌ Don't Create Custom When:**
- **Standard patterns**: Use `IsOwnerOrAdmin` instead of custom similar logic
- **Simple admin checks**: Use `IsAdminUser` or `IsAdminOrReadOnly`
- **Basic authentication**: Use `permissions.IsAuthenticated`

## 📂 **File Organization**

### **Core Permissions**
```
core/
├── permissions/
│   ├── __init__.py       # Export all permissions
│   ├── base.py          # All permission implementations
│   └── README.md        # Permission documentation
```

### **App-specific Permissions**
```python
# ONLY when you need truly app-specific logic
app_name/
├── permissions.py       # Only custom permissions
├── views.py            # Import from core.permissions  
└── viewsets.py         # Import from core.permissions
```

## 🔄 **Migration from App-specific to Core**

### **Step 1: Identify Duplicates**
```bash
# Tìm duplicate permissions
grep -r "class IsAdminOrReadOnly" */permissions.py
grep -r "class IsOwnerOrAdmin" */permissions.py
```

### **Step 2: Update Imports**
```python
# Before
from .permissions import IsOwnerOrAdmin

# After  
from core.permissions import IsOwnerOrAdmin
```

### **Step 3: Remove Duplicates**
```python
# Delete duplicate permission classes từ app-specific files
# Giữ lại chỉ permissions thực sự cần thiết cho app đó
```

## 🚀 **Performance Considerations**

### **Efficient Permission Checking**
```python
# ✅ Good: Use efficient object-level permissions
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Fast check with database hits minimized
        if request.user.is_staff:
            return True
        return obj.user == request.user

# ❌ Bad: Multiple database queries in permission
def has_object_permission(self, request, view, obj):
    user_profile = request.user.profile  # DB hit
    related_objects = obj.related.all()  # DB hit
    # Complex logic with multiple queries
```

### **Queryset Optimization**
```python
# Optimize queryset trong ViewSet thay vì permission
def get_queryset(self):
    queryset = super().get_queryset()
    if not self.request.user.is_staff:
        queryset = queryset.filter(user=self.request.user)
    return queryset
```

## 📊 **Permission Usage Statistics**

### **Current Adoption**
- **IsAdminOrReadOnly**: 80% adoption ✅
- **IsOwnerOrReadOnly**: 70% adoption ✅  
- **IsOwnerOrAdmin**: 60% adoption ⚠️
- **IsSellerOrAdmin**: 20% adoption (new) 🆕
- **IsOwner**: 40% adoption ⚠️

### **Migration Status**
- ✅ **support** app: Migrated to core permissions
- ✅ **customers** app: Partially migrated
- ✅ **promotions** app: Partially migrated
- 🔄 **reviews, products, orders**: Need standardization
- 🔄 **cart, catalog, hrm**: Need standardization

## 🎯 **Action Items for Developers**

### **For New Features**
1. **Always check** `core.permissions` first
2. **Use PermissionByActionMixin** for complex permission logic
3. **Write tests** for permission logic
4. **Document** any custom permissions needed

### **For Existing Code**
1. **Audit** existing app-specific permissions
2. **Migrate** duplicates to core permissions
3. **Standardize** import patterns
4. **Update** tests to use core permissions

## 🆘 **Common Issues & Solutions**

### **Issue: Import Error**
```python
# Error: ImportError: cannot import name 'IsOwnerOrAdmin'
# Solution: Check if permission exists in core.permissions.__init__.py
from core.permissions import IsOwnerOrAdmin  # ✅
```

### **Issue: Permission Not Working**
```python
# Check: Does your ViewSet inherit from correct base?
class MyViewSet(StandardizedModelViewSet):  # ✅
    permission_classes = [IsOwnerOrAdmin]
```

### **Issue: Object Permission Not Called**
```python
# Check: Are you using object-level endpoints?
# Object permissions only work on detail views (retrieve, update, destroy)
# NOT on list views (list, create)
```

## 📞 **Support & Questions**

- **Documentation**: `docs/PERMISSION_USAGE_GUIDE.md`
- **Examples**: Look at `users`, `products`, `orders` apps
- **Tests**: `core/tests/test_permissions.py`
- **Issues**: Create GitHub issue với tag `permissions`

---

## 🎉 **Summary**

- ✅ **Use core permissions** whenever possible
- ✅ **Import từ core.permissions** (không phải .base)
- ✅ **Combine với PermissionByActionMixin** cho complex logic
- ✅ **Test permissions** thoroughly
- ✅ **Document custom permissions** when needed

**Remember**: Consistency is key! Follow the established patterns để maintain clean, testable, và scalable permission system. 🚀 