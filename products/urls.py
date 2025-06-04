from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    ProductPublicViewSet, ProductUserViewSet, 
    ProductSellerViewSet, ProductAdminViewSet
)

app_name = 'products'

# Router chính
router = DefaultRouter(trailing_slash=False)

# Admin endpoints
router.register(r'admin', ProductAdminViewSet, basename='product-admin')

# URL patterns
urlpatterns = [
    # Admin router URLs
    path('', include(router.urls)),
    
    # Public product endpoints (no auth required)
    # /api/v1/products/ - Public product listing và detail
    path('', ProductPublicViewSet.as_view({
        'get': 'list',        # GET /api/v1/products/ - Danh sách products public
    }), name='product-public-list'),
    
    path('<int:pk>/', ProductPublicViewSet.as_view({
        'get': 'retrieve',    # GET /api/v1/products/{id}/ - Chi tiết product public
    }), name='product-public-detail'),
    
    # Public special endpoints
    path('featured/', ProductPublicViewSet.as_view({
        'get': 'featured'     # GET /api/v1/products/featured/ - Products nổi bật
    }), name='product-featured'),
    
    path('trending/', ProductPublicViewSet.as_view({
        'get': 'trending'     # GET /api/v1/products/trending/ - Products trending
    }), name='product-trending'),
    
    # User features endpoints (require auth)
    # /api/v1/products/me/ - User product features
    path('me/favorites/', ProductUserViewSet.as_view({
        'get': 'list_favorites',   # GET /api/v1/products/me/favorites/ - Xem favorites
        'post': 'add_favorite',    # POST /api/v1/products/me/favorites/ - Thêm favorite
    }), name='product-user-favorites'),
    
    path('me/favorites/<int:pk>/', ProductUserViewSet.as_view({
        'delete': 'remove_favorite'  # DELETE /api/v1/products/me/favorites/{id}/ - Xóa favorite
    }), name='product-user-favorite-detail'),
    
    path('me/recently-viewed/', ProductUserViewSet.as_view({
        'get': 'recently_viewed'  # GET /api/v1/products/me/recently-viewed/ - Recently viewed
    }), name='product-user-recent'),
    
    path('me/recommendations/', ProductUserViewSet.as_view({
        'get': 'recommendations'  # GET /api/v1/products/me/recommendations/ - Recommendations
    }), name='product-user-recommendations'),
    
    # Seller product management endpoints
    # /api/v1/products/my-products/ - Seller product management
    path('my-products/', ProductSellerViewSet.as_view({
        'get': 'list',       # GET /api/v1/products/my-products/ - Products của seller
        'post': 'create',    # POST /api/v1/products/my-products/ - Tạo product mới
    }), name='product-seller-list'),
    
    path('my-products/<int:pk>/', ProductSellerViewSet.as_view({
        'get': 'retrieve',   # GET /api/v1/products/my-products/{id}/ - Chi tiết product
        'put': 'update',     # PUT /api/v1/products/my-products/{id}/ - Cập nhật product
        'patch': 'partial_update',  # PATCH /api/v1/products/my-products/{id}/ - Partial update
        'delete': 'destroy'  # DELETE /api/v1/products/my-products/{id}/ - Xóa product
    }), name='product-seller-detail'),
    
    # Seller product image management
    path('my-products/<int:pk>/upload-image/', ProductSellerViewSet.as_view({
        'post': 'upload_image'  # POST /api/v1/products/my-products/{id}/upload-image/ - Upload image
    }), name='product-seller-upload-image'),
    
    # Seller analytics
    path('my-products/analytics/', ProductSellerViewSet.as_view({
        'get': 'analytics'   # GET /api/v1/products/my-products/analytics/ - Overview analytics
    }), name='product-seller-analytics'),
    
    path('my-products/<int:pk>/analytics/', ProductSellerViewSet.as_view({
        'get': 'analytics_detail'  # GET /api/v1/products/my-products/{id}/analytics/ - Product analytics
    }), name='product-seller-analytics-detail'),
]
