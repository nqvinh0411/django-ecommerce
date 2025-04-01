from django.urls import path
from .views import (
    SalesReportListView,
    ProductReportListView,
    CustomerReportListView,
    TrafficLogListView
)

urlpatterns = [
    path('sales/', SalesReportListView.as_view(), name='sales-report'),
    path('products/', ProductReportListView.as_view(), name='product-report'),
    path('customers/', CustomerReportListView.as_view(), name='customer-report'),
    path('traffic/', TrafficLogListView.as_view(), name='traffic-log'),
]
