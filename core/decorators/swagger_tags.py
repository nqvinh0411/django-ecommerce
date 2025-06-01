"""
Decorators để tự động thêm tags cho Swagger UI documentation.
"""
from functools import wraps
from drf_yasg.utils import swagger_auto_schema


def swagger_tag_decorator(tag_name):
    """
    Decorator để thêm tag cho API endpoint trong Swagger UI.
    
    Args:
        tag_name: Tên module/tag sẽ hiển thị trong Swagger UI
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, *args, **kwargs):
            if hasattr(view, 'swagger_auto_schema'):
                original_schema = getattr(view, 'swagger_auto_schema', {})
                if isinstance(original_schema, dict):
                    original_schema['tags'] = [tag_name]
                    view.swagger_auto_schema = original_schema
            return view_func(view, *args, **kwargs)
        return _wrapped_view
    return decorator


class SwaggerTagMixin:
    """
    Mixin để thêm Swagger tag cho ViewSet và APIView.
    Sử dụng trong các class-based views để thêm tag tự động.
    """
    swagger_tag = None
    
    def get_swagger_tag(self):
        """Lấy tên tag từ thuộc tính của class hoặc từ tên model."""
        if self.swagger_tag:
            return self.swagger_tag
        
        # Tự động lấy từ tên model nếu có
        if hasattr(self, 'queryset') and self.queryset is not None:
            model = self.queryset.model
            return model._meta.verbose_name.title()
        
        # Fallback to class name
        return self.__class__.__name__
    
    @swagger_auto_schema(tags=['default'])
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch để thêm tag."""
        self.swagger_auto_schema.tags = [self.get_swagger_tag()]
        return super().dispatch(request, *args, **kwargs)


def apply_swagger_tags(viewset_class, tag_name):
    """
    Function để áp dụng swagger tag cho một viewset/view.
    
    Args:
        viewset_class: Class view/viewset cần áp dụng tag
        tag_name: Tên tag sẽ hiển thị trong Swagger
        
    Returns:
        Class đã được áp dụng tag
    """
    # Lưu các method hiện có
    existing_methods = {}
    for method_name in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
        if hasattr(viewset_class, method_name):
            existing_methods[method_name] = getattr(viewset_class, method_name)
    
    # Áp dụng swagger_auto_schema với tags
    for method_name, method in existing_methods.items():
        setattr(viewset_class, method_name, swagger_auto_schema(tags=[tag_name])(method))
    
    return viewset_class
