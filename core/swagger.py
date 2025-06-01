"""
Cấu hình Swagger UI và ReDoc cho API Documentation.

Module này cung cấp các cấu hình và view cần thiết cho việc tích hợp
Swagger UI và ReDoc vào dự án để hiển thị tài liệu API.
"""
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema


class CustomSchemaGenerator(SchemaGenerator):
    """
    Custom schema generator để tùy chỉnh cách tạo schema cho API documentation.
    """
    
    def get_paths(self, request=None):
        """
        Override để tùy chỉnh cách tạo paths trong schema.
        """
        paths = super().get_paths(request)
        
        # Tùy chỉnh paths nếu cần
        return paths


class CustomAutoSchema(AutoSchema):
    """
    Custom auto schema để tùy chỉnh cách tạo schema cho từng endpoint.
    """
    
    def get_tags(self):
        """
        Override để ưu tiên manual tags từ @extend_schema decorator.
        """
        # Lấy tags từ decorator trước
        if hasattr(self.view, 'get_tags'):
            return self.view.get_tags()
        
        # Fallback về tags mặc định
        return super().get_tags()


# Định nghĩa tags theo module
API_TAGS = [
    {"name": "Authentication", "description": "Các endpoint xác thực và phân quyền"},
    {"name": "Products", "description": "Các endpoint quản lý sản phẩm"},
    {"name": "Categories", "description": "Các endpoint quản lý danh mục sản phẩm"},
    {"name": "Cart", "description": "Các endpoint quản lý giỏ hàng"},
    {"name": "Orders", "description": "Các endpoint quản lý đơn hàng"},
    {"name": "Customers", "description": "Các endpoint quản lý khách hàng"},
    {"name": "Users", "description": "Các endpoint quản lý người dùng"},
    {"name": "Payments", "description": "Các endpoint quản lý thanh toán"},
    {"name": "Shipping", "description": "Các endpoint quản lý vận chuyển"},
    {"name": "Inventory", "description": "Các endpoint quản lý kho hàng"},
    {"name": "Reviews", "description": "Các endpoint quản lý đánh giá sản phẩm"},
    {"name": "Wishlist", "description": "Các endpoint quản lý danh sách yêu thích"},
    {"name": "Promotions", "description": "Các endpoint quản lý khuyến mãi"},
    {"name": "Notifications", "description": "Các endpoint quản lý thông báo"},
    {"name": "Support", "description": "Các endpoint hỗ trợ khách hàng"},
    {"name": "Reports", "description": "Các endpoint báo cáo và thống kê"},
    {"name": "Settings", "description": "Các endpoint cấu hình hệ thống"},
    {"name": "HRM", "description": "Các endpoint quản lý nhân sự"},
    {"name": "Pages", "description": "Các endpoint quản lý trang tĩnh"},
]

# Mapping để nhóm các endpoints theo chức năng
ENDPOINT_GROUPS = {
    'Authentication': {
        'patterns': ['/auth', '/users/login', '/users/register'],
        'tags': ['Authentication']
    },
    'Product Management': {
        'patterns': ['/products', '/categories', '/inventory'],
        'tags': ['Products', 'Categories', 'Inventory']
    },
    'E-commerce Operations': {
        'patterns': ['/cart', '/orders', '/payments', '/shipping', '/promotions'],
        'tags': ['Cart', 'Orders', 'Payments', 'Shipping', 'Promotions']
    },
    'Customer Management': {
        'patterns': ['/customers', '/users', '/reviews', '/wishlist', '/notifications', '/support'],
        'tags': ['Customers', 'Users', 'Reviews', 'Wishlist', 'Notifications', 'Support']
    },
    'Administration': {
        'patterns': ['/reports', '/settings', '/hrm', '/pages'],
        'tags': ['Reports', 'Settings', 'HRM', 'Pages']
    }
}


def custom_preprocessing_hook(endpoints):
    """
    Hook để xử lý trước khi generate schema.
    Nhóm các endpoints theo chức năng.
    """
    return endpoints


def custom_postprocessing_hook(result, generator, request, public):
    """
    Hook để xử lý sau khi generate schema.
    Tạo ra cấu trúc nhóm trong schema.
    """
    return result
