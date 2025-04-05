from django.urls import path

from .views import (
    CartDetailView, CartItemCreateView, CartItemUpdateView, 
    CartItemDeleteView, CartClearView
)

app_name = 'cart'

urlpatterns = [
    # Cart endpoints
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('items', CartItemCreateView.as_view(), name='cart-item-create'),
    path('items/<int:item_id>', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('items/<int:item_id>/delete', CartItemDeleteView.as_view(), name='cart-item-delete'),
    path('clear', CartClearView.as_view(), name='cart-clear'),
]
