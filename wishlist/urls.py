from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import WishlistViewSet

# Legacy imports for backward compatibility
from .views import (
    WishlistRetrieveView,
    WishlistItemListView,
    WishlistItemCreateView,
    WishlistItemRetrieveView,
    WishlistItemDestroyView
)

app_name = "wishlist"

# Thiết lập router cho ViewSets
router = DefaultRouter(trailing_slash=False)
router.register(r'', WishlistViewSet, basename='wishlist')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Wishlist endpoints - DEPRECATED
    path('/old/wishlist/view', WishlistRetrieveView.as_view(), name='wishlist-detail-legacy'),
    path('/old/wishlist/items/list', WishlistItemListView.as_view(), name='wishlist-items-list-legacy'),
    path('/old/wishlist/items/add', WishlistItemCreateView.as_view(), name='wishlist-items-create-legacy'),
    path('/old/wishlist/items/<int:item_id>/view', WishlistItemRetrieveView.as_view(), name='wishlist-item-detail-legacy'),
    path('/old/wishlist/items/<int:item_id>/remove', WishlistItemDestroyView.as_view(), name='wishlist-item-delete-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
