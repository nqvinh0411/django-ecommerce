from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import ProductViewSet

# Legacy imports for backward compatibility
from .views import (
    ProductListView, ProductCreateView,
    ProductRetrieveView, ProductUpdateView, ProductDestroyView, ProductImageUploadView
)

app_name = 'products'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Product endpoints - DEPRECATED
    path('/old/list', ProductListView.as_view(), name='list-legacy'),
    path('/old/create', ProductCreateView.as_view(), name='create-legacy'),
    path('/old/<int:pk>/view', ProductRetrieveView.as_view(), name='detail-legacy'),
    path('/old/<int:pk>/update', ProductUpdateView.as_view(), name='update-legacy'),
    path('/old/<int:pk>/delete', ProductDestroyView.as_view(), name='delete-legacy'),

    # Product image endpoints - DEPRECATED
    path('/old/<int:product_id>/images/upload', ProductImageUploadView.as_view(), name='image-upload-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
