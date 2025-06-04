from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import OrderViewSet, OrderSelfViewSet

app_name = 'orders'

# Router chính
router = DefaultRouter(trailing_slash=False)

# Admin endpoints
router.register(r'admin', OrderViewSet, basename='order-admin')

# URL patterns
urlpatterns = [
    # Admin router URLs
    path('', include(router.urls)),
    
    # User self-management endpoints
    # /api/v1/orders/me/ - Order management của user hiện tại
    path('me/', OrderSelfViewSet.as_view({
        'get': 'list',      # GET /api/v1/orders/me/ - Danh sách đơn hàng
        'post': 'create',   # POST /api/v1/orders/me/ - Tạo đơn hàng mới
    }), name='order-self-list'),
    
    path('me/<int:pk>/', OrderSelfViewSet.as_view({
        'get': 'retrieve',  # GET /api/v1/orders/me/{id}/ - Chi tiết đơn hàng
        'put': 'update',    # PUT /api/v1/orders/me/{id}/ - Cập nhật đơn hàng
        'patch': 'partial_update'  # PATCH /api/v1/orders/me/{id}/ - Partial update
    }), name='order-self-detail'),
    
    # Order actions
    path('me/<int:pk>/cancel/', OrderSelfViewSet.as_view({
        'post': 'cancel'    # POST /api/v1/orders/me/{id}/cancel/ - Hủy đơn hàng
    }), name='order-self-cancel'),
    
    # Order history
    path('me/history/', OrderSelfViewSet.as_view({
        'get': 'history'    # GET /api/v1/orders/me/history/ - Lịch sử đơn hàng
    }), name='order-self-history'),
]
