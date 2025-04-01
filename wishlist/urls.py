from django.urls import path
from .views import WishlistView, AddWishlistItemView, RemoveWishlistItemView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist-view'),
    path('add/', AddWishlistItemView.as_view(), name='wishlist-add'),
    path('remove/<int:item_id>/', RemoveWishlistItemView.as_view(), name='wishlist-remove'),
]
