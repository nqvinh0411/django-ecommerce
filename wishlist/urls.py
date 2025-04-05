from django.urls import path
from .views import (
    WishlistRetrieveView,
    WishlistItemListView,
    WishlistItemCreateView,
    WishlistItemRetrieveView,
    WishlistItemDestroyView
)

app_name = "wishlist"

urlpatterns = [
    # GET /wishlist/view - Lấy thông tin wishlist của người dùng hiện tại
    path('wishlist/view', WishlistRetrieveView.as_view(), name='wishlist-detail'),
    
    # GET /wishlist/items/list - Lấy danh sách các items trong wishlist
    path('wishlist/items/list', WishlistItemListView.as_view(), name='wishlist-items-list'),
    
    # POST /wishlist/items/add - Thêm sản phẩm vào wishlist
    path('wishlist/items/add', WishlistItemCreateView.as_view(), name='wishlist-items-create'),
    
    # GET /wishlist/items/{id}/view - Lấy chi tiết một item cụ thể
    path('wishlist/items/<int:item_id>/view', WishlistItemRetrieveView.as_view(), name='wishlist-item-detail'),
    
    # DELETE /wishlist/items/{id}/remove - Xóa một item khỏi wishlist
    path('wishlist/items/<int:item_id>/remove', WishlistItemDestroyView.as_view(), name='wishlist-item-delete'),
]
