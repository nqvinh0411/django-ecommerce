from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import ReviewSelfViewSet, ReviewAdminViewSet, ProductReviewViewSet

# Legacy imports for backward compatibility
from .views import (
    ReviewCreateView, ProductReviewListView, 
    UserReviewListView, ReviewDetailView
)

app_name = 'reviews'

# Router chính
router = DefaultRouter()

# Admin endpoints
router.register(r'admin', ReviewAdminViewSet, basename='review-admin')

# URL patterns
urlpatterns = [
    # Admin router URLs
    path('', include(router.urls)),
    
    # User self-management endpoints
    # /api/v1/reviews/me/ - Review management của user hiện tại
    path('me/', ReviewSelfViewSet.as_view({
        'get': 'list',      # GET /api/v1/reviews/me/ - Danh sách reviews của mình
        'post': 'create',   # POST /api/v1/reviews/me/ - Tạo review mới
    }), name='review-self-list'),
    
    path('me/<int:pk>/', ReviewSelfViewSet.as_view({
        'get': 'retrieve',  # GET /api/v1/reviews/me/{id}/ - Chi tiết review
        'put': 'update',    # PUT /api/v1/reviews/me/{id}/ - Cập nhật review
        'patch': 'partial_update',  # PATCH /api/v1/reviews/me/{id}/ - Partial update
        'delete': 'destroy' # DELETE /api/v1/reviews/me/{id}/ - Xóa review
    }), name='review-self-detail'),
    
    # User product reviews
    path('me/products/<int:product_id>/', ReviewSelfViewSet.as_view({
        'get': 'product_review'  # GET /api/v1/reviews/me/products/{id}/ - Review của mình cho sản phẩm
    }), name='review-self-product'),
    
    # Public product reviews endpoints
    path('products/<int:product_id>/', ProductReviewViewSet.as_view({
        'get': 'list'       # GET /api/v1/reviews/products/{id}/ - Reviews của sản phẩm
    }), name='product-reviews'),
    
    path('products/<int:product_id>/stats/', ProductReviewViewSet.as_view({
        'get': 'stats'      # GET /api/v1/reviews/products/{id}/stats/ - Thống kê reviews
    }), name='product-review-stats'),
    
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
