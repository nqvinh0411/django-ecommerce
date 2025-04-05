from django.urls import path
from .views import (
    SalesReportListView,
    ProductReportListView,
    CustomerReportListView,
    TrafficLogListView
)

app_name = "reports"

urlpatterns = [
    # Sales reports - GET (list)
    path('sales', SalesReportListView.as_view(), name='sales-report'),
    
    # Product reports - GET (list)
    path('products', ProductReportListView.as_view(), name='product-report'),
    
    # Customer reports - GET (list)
    path('customers', CustomerReportListView.as_view(), name='customer-report'),
    
    # Traffic logs - GET (list)
    path('traffic', TrafficLogListView.as_view(), name='traffic-log'),
]
