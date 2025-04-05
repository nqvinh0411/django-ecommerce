"""
Sales Report views module
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import SalesReport
from ..serializers import SalesReportSerializer


class SalesReportListView(generics.ListAPIView):
    """
    API view để liệt kê báo cáo doanh số.
    
    GET /reports/sales - Liệt kê báo cáo doanh số
    
    Chỉ admin mới có thể truy cập.
    Hỗ trợ lọc theo ngày và sắp xếp theo nhiều tiêu chí.
    """
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_orders', 'total_revenue', 'net_revenue']
    ordering = ['-date']
