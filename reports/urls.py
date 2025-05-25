from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    SalesReportViewSet, ProductReportViewSet,
    CustomerReportViewSet, TrafficLogViewSet
)

# Legacy imports for backward compatibility
from .views import (
    SalesReportListView,
    ProductReportListView,
    CustomerReportListView,
    TrafficLogListView
)

app_name = "reports"

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'sales', SalesReportViewSet, basename='sales-report')
router.register(r'products', ProductReportViewSet, basename='product-report')
router.register(r'customers', CustomerReportViewSet, basename='customer-report')
router.register(r'traffic', TrafficLogViewSet, basename='traffic-log')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Legacy report endpoints - DEPRECATED
    path('/old/sales', SalesReportListView.as_view(), name='sales-report-legacy'),
    path('/old/products', ProductReportListView.as_view(), name='product-report-legacy'),
    path('/old/customers', CustomerReportListView.as_view(), name='customer-report-legacy'),
    path('/old/traffic', TrafficLogListView.as_view(), name='traffic-log-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
