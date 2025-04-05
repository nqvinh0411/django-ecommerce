"""
Customer Report views module
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import CustomerReport
from ..serializers import CustomerReportSerializer


class CustomerReportListView(generics.ListAPIView):
    """
    API view để liệt kê báo cáo khách hàng.
    
    GET /reports/customers - Liệt kê báo cáo khách hàng
    
    Chỉ admin mới có thể truy cập.
    Hỗ trợ tìm kiếm, lọc và sắp xếp theo nhiều tiêu chí.
    """
    queryset = CustomerReport.objects.all()
    serializer_class = CustomerReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['last_order_at']
    search_fields = [
        'customer__user__email', 'customer__user__first_name',
        'customer__user__last_name', 'customer__phone_number'
    ]
    ordering_fields = [
        'total_orders', 'total_spent', 'average_order_value', 'last_order_at'
    ]
    ordering = ['-total_spent']
