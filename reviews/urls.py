from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import ReviewViewSet

# Legacy imports for backward compatibility
from .views import (
    ReviewCreateView, ProductReviewListView, 
    UserReviewListView, ReviewDetailView
)

app_name = 'reviews'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Review endpoints - DEPRECATED
    path('/old/create', ReviewCreateView.as_view(), name='review-create-legacy'),
    path('/old/products/<int:product_id>', ProductReviewListView.as_view(), name='product-reviews-legacy'),
    path('/old/my-reviews', UserReviewListView.as_view(), name='user-reviews-legacy'),
    path('/old/<int:review_id>', ReviewDetailView.as_view(), name='review-detail-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
