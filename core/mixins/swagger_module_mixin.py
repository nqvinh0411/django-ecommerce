"""
Swagger Module Mixin

Mixin này tự động áp dụng tag cho các viewsets trong Swagger UI dựa trên module.
Nó giúp tổ chức tài liệu API theo module để dễ đọc và tìm kiếm hơn.
"""
from functools import wraps
from drf_yasg.utils import swagger_auto_schema

# Dictionary ánh xạ tên module sang tên tag hiển thị
MODULE_TAG_MAPPING = {
    'products': 'Products',
    'cart': 'Cart',
    'orders': 'Orders',
    'payments': 'Payments', 
    'reviews': 'Reviews',
    'notifications': 'Notifications',
    'catalog': 'Catalog',
    'customers': 'Customers',
    'inventory': 'Inventory',
    'shipping': 'Shipping',
    'promotions': 'Promotions',
    'wishlist': 'Wishlist',
    'users': 'Users',
    'reports': 'Reports',
    'settings': 'Settings',
    'pages': 'Pages',
    'support': 'Support',
    'hrm': 'HRM',
}

def swagger_module_decorator(module=None):
    """
    Decorator để thêm tag module cho một class-based view hoặc viewset.
    
    Args:
        module: Tên module sẽ sử dụng làm tag. Nếu là None, sẽ tự động
               lấy từ tên của module chứa view.
    """
    def decorator(view_class):
        # Xác định module tag
        module_name = module
        if module_name is None:
            # Tự động lấy từ tên module
            module_path = view_class.__module__.split('.')
            if module_path:
                module_name = module_path[0]
        
        # Lấy tên tag hiển thị từ mapping hoặc dùng tên module nếu không có
        tag_name = MODULE_TAG_MAPPING.get(module_name, module_name.capitalize())
        
        # Áp dụng swagger_auto_schema cho các methods phổ biến của viewset
        methods = [
            'list', 'retrieve', 'create', 'update', 
            'partial_update', 'destroy', 'get', 
            'post', 'put', 'patch', 'delete'
        ]
        
        # Lặp qua các method và áp dụng tag
        for method_name in methods:
            if hasattr(view_class, method_name):
                method = getattr(view_class, method_name)
                decorated_method = swagger_auto_schema(tags=[tag_name])(method)
                setattr(view_class, method_name, decorated_method)
        
        # Xử lý các action tùy chỉnh
        for attr_name in dir(view_class):
            attr = getattr(view_class, attr_name)
            if hasattr(attr, 'mapping') and callable(attr):
                decorated_action = swagger_auto_schema(tags=[tag_name])(attr)
                setattr(view_class, attr_name, decorated_action)
                
        return view_class
    return decorator


class SwaggerModuleMixin:
    """
    Mixin tự động áp dụng tag Swagger cho viewset dựa trên module.
    
    Cách sử dụng:
        class ProductViewSet(SwaggerModuleMixin, ModelViewSet):
            swagger_tag = 'Products'  # Tùy chọn, nếu không sẽ tự động lấy từ tên module
    """
    swagger_tag = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_swagger_tag()
    
    def _apply_swagger_tag(self):
        """Áp dụng tag cho tất cả các methods."""
        # Xác định tag
        tag = self.swagger_tag
        if tag is None:
            module_name = self.__module__.split('.')[0]
            tag = MODULE_TAG_MAPPING.get(module_name, module_name.capitalize())
            
        # Áp dụng cho các methods chuẩn của viewset
        methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
        for method_name in methods:
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    setattr(self, method_name, swagger_auto_schema(tags=[tag])(method))
