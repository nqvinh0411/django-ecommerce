from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import CartViewSet

# Legacy imports for backward compatibility
from .views import (
    CartDetailView, CartItemCreateView, CartItemUpdateView, 
    CartItemDeleteView, CartClearView
)

app_name = 'cart'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
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
