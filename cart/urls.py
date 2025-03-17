from django.urls import path

from .views import CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('update/', UpdateCartItemView.as_view(), name='cart-update'),
    path('remove/', RemoveFromCartView.as_view(), name='cart-remove'),
]
