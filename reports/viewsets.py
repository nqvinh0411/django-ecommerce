"""
Reports API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Reports API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from core.viewsets.base import StandardizedModelViewSet
from drf_spectacular.utils import extend_schema
from .models import SalesReport, ProductReport, CustomerReport, TrafficLog
from .serializers import (
    SalesReportSerializer, ProductReportSerializer,
    CustomerReportSerializer, TrafficLogSerializer
)
from .permissions import IsAdminUserForReports


@extend_schema(tags=['Reports'])
class SalesReportViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý SalesReport resources.
    
    Cung cấp các endpoints để xem báo cáo doanh số bán hàng.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/sales/ - Liệt kê tất cả báo cáo doanh số
    - GET /api/v1/reports/sales/{id}/ - Xem chi tiết báo cáo doanh số
    - GET /api/v1/reports/sales/summary/ - Xem tổng quan doanh số
    """
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [IsAdminUserForReports]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_orders', 'total_revenue', 'net_revenue']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Tổng quan doanh số trong một khoảng thời gian.
        """
        # Lấy khoảng thời gian từ query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Lọc báo cáo theo khoảng thời gian
        queryset = self.queryset
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Tính tổng
        total_orders = 0
        total_revenue = 0
        total_discount = 0
        net_revenue = 0
        
        for report in queryset:
            total_orders += report.total_orders
            total_revenue += report.total_revenue
            total_discount += report.total_discount
            net_revenue += report.net_revenue
        
        # Trả về kết quả
        summary_data = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'total_discount': float(total_discount),
            'net_revenue': float(net_revenue),
            'report_count': queryset.count()
        }
        
        return self.success_response(
            data=summary_data,
            message="Tổng quan doanh số",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Reports'])
class ProductReportViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý ProductReport resources.
    
    Cung cấp các endpoints để xem báo cáo hiệu suất sản phẩm.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/products/ - Liệt kê tất cả báo cáo sản phẩm
    - GET /api/v1/reports/products/{id}/ - Xem chi tiết báo cáo sản phẩm
    - GET /api/v1/reports/products/top-selling/ - Xem các sản phẩm bán chạy nhất
    """
    queryset = ProductReport.objects.all()
    serializer_class = ProductReportSerializer
    permission_classes = [IsAdminUserForReports]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product']
    search_fields = ['product__name']
    ordering_fields = ['sold_quantity', 'total_revenue', 'average_rating', 'last_sold_at']
    ordering = ['-sold_quantity']
    
    @action(detail=False, methods=['get'], url_path='top-selling')
    def top_selling(self, request):
        """
        Lấy danh sách sản phẩm bán chạy nhất.
        """
        # Lấy số lượng sản phẩm hiển thị từ query parameters, mặc định là 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # Lấy danh sách sản phẩm bán chạy nhất
        queryset = self.queryset.order_by('-sold_quantity')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message=f"{limit} sản phẩm bán chạy nhất",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Reports'])
class CustomerReportViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý CustomerReport resources.
    
    Cung cấp các endpoints để xem báo cáo hiệu suất khách hàng.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/customers/ - Liệt kê tất cả báo cáo khách hàng
    - GET /api/v1/reports/customers/{id}/ - Xem chi tiết báo cáo khách hàng
    - GET /api/v1/reports/customers/top-spenders/ - Xem khách hàng chi tiêu nhiều nhất
    """
    queryset = CustomerReport.objects.all()
    serializer_class = CustomerReportSerializer
    permission_classes = [IsAdminUserForReports]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer']
    search_fields = ['customer__user__email', 'customer__user__first_name', 'customer__user__last_name']
    ordering_fields = ['total_orders', 'total_spent', 'average_order_value', 'last_order_at']
    ordering = ['-total_spent']
    
    @action(detail=False, methods=['get'], url_path='top-spenders')
    def top_spenders(self, request):
        """
        Lấy danh sách khách hàng chi tiêu nhiều nhất.
        """
        # Lấy số lượng khách hàng hiển thị từ query parameters, mặc định là 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # Lấy danh sách khách hàng chi tiêu nhiều nhất
        queryset = self.queryset.order_by('-total_spent')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message=f"{limit} khách hàng chi tiêu nhiều nhất",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Reports'])
class TrafficLogViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý TrafficLog resources.
    
    Cung cấp các endpoints để xem nhật ký truy cập API.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/traffic/ - Liệt kê tất cả nhật ký truy cập
    - GET /api/v1/reports/traffic/{id}/ - Xem chi tiết nhật ký truy cập
    - GET /api/v1/reports/traffic/slow-endpoints/ - Xem các endpoint chậm nhất
    """
    queryset = TrafficLog.objects.all()
    serializer_class = TrafficLogSerializer
    permission_classes = [IsAdminUserForReports]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['endpoint', 'method', 'ip_address']
    search_fields = ['endpoint', 'user_agent']
    ordering_fields = ['timestamp', 'duration_ms']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'], url_path='slow-endpoints')
    def slow_endpoints(self, request):
        """
        Lấy danh sách các endpoint chậm nhất.
        """
        # Lấy số lượng endpoint hiển thị từ query parameters, mặc định là 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # Lấy khoảng thời gian từ query parameters
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        # Lọc nhật ký theo khoảng thời gian
        queryset = self.queryset
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
        
        # Lấy các endpoint chậm nhất
        queryset = queryset.order_by('-duration_ms')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message=f"{limit} endpoint chậm nhất",
            status_code=status.HTTP_200_OK
        )
