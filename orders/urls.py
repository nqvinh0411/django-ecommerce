from django.urls import path
from .views import CreateOrderView, UserOrdersView, OrderDetailView, UpdateOrderStatusView

app_name = 'orders'

urlpatterns = [
    path('create', CreateOrderView.as_view(), name='order-create'),
    path('', UserOrdersView.as_view(), name='order-list'),
    path('<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/update-status', UpdateOrderStatusView.as_view(), name='order-update-status'),
]
