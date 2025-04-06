from django.urls import path
from .views import (
    OrderCreateView, UserOrderListView, OrderDetailView, 
    OrderStatusUpdateView
)

app_name = 'orders'

urlpatterns = [
    # Các endpoints cho đơn hàng
    path('', UserOrderListView.as_view(), name='order-list'),
    path('create', OrderCreateView.as_view(), name='order-create'),
    path('<int:order_id>', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/status', OrderStatusUpdateView.as_view(), name='order-status-update'),
]
