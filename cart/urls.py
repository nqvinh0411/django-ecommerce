from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import CartSelfViewSet, CartAdminViewSet, CartItemAdminViewSet

# Legacy imports for backward compatibility
from .views import (
    CartDetailView, CartItemCreateView, CartItemUpdateView, 
    CartItemDeleteView, CartClearView
)

app_name = 'cart'

# Router chính
router = DefaultRouter()

# Admin endpoints
router.register(r'admin', CartAdminViewSet, basename='cart-admin')
router.register(r'admin/items', CartItemAdminViewSet, basename='cart-item-admin')

# URL patterns
urlpatterns = [
    # Admin router URLs
    path('', include(router.urls)),
    
    # User self-management endpoints
    # /api/v1/cart/me/ - Cart management của user hiện tại
    path('me/', CartSelfViewSet.as_view({
        'get': 'list',      # GET /api/v1/cart/me/ - Xem giỏ hàng
    }), name='cart-self'),
    
    # Cart summary
    path('me/summary/', CartSelfViewSet.as_view({
        'get': 'summary'    # GET /api/v1/cart/me/summary/ - Tóm tắt giỏ hàng
    }), name='cart-self-summary'),
    
    # Cart items management
    path('me/items/', CartSelfViewSet.as_view({
        'post': 'add_item' # POST /api/v1/cart/me/items/ - Thêm sản phẩm
    }), name='cart-self-add-item'),
    
    path('me/items/<int:item_id>/', CartSelfViewSet.as_view({
        'put': 'update_item',      # PUT /api/v1/cart/me/items/{id}/ - Cập nhật
        'patch': 'update_item',    # PATCH /api/v1/cart/me/items/{id}/ - Cập nhật
        'delete': 'remove_item'    # DELETE /api/v1/cart/me/items/{id}/ - Xóa item
    }), name='cart-self-item'),
    
    # Cart actions
    path('me/clear/', CartSelfViewSet.as_view({
        'delete': 'clear'   # DELETE /api/v1/cart/me/clear/ - Xóa tất cả
    }), name='cart-self-clear'),
    
    path('me/checkout/', CartSelfViewSet.as_view({
        'post': 'checkout'  # POST /api/v1/cart/me/checkout/ - Checkout
    }), name='cart-self-checkout'),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Cart endpoints - DEPRECATED
    path('/old', CartDetailView.as_view(), name='cart-detail-legacy'),
    path('/old/items/create', CartItemCreateView.as_view(), name='cart-item-create-legacy'),
    path('/old/items/<int:item_id>/update', CartItemUpdateView.as_view(), name='cart-item-update-legacy'),
    path('/old/items/<int:item_id>/delete', CartItemDeleteView.as_view(), name='cart-item-delete-legacy'),
    path('/old/clear', CartClearView.as_view(), name='cart-clear-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
