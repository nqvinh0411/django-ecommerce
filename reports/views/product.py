"""
Product Report views module
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import ProductReport
from ..serializers import ProductReportSerializer


class ProductReportListView(generics.ListAPIView):
    """
    API view để liệt kê báo cáo sản phẩm.
    
    GET /reports/products - Liệt kê báo cáo sản phẩm
    
    Chỉ admin mới có thể truy cập.
    Hỗ trợ tìm kiếm, lọc và sắp xếp theo nhiều tiêu chí.
    """
    queryset = ProductReport.objects.all()
    serializer_class = ProductReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['last_sold_at']
    search_fields = ['product__name', 'product__description']
    ordering_fields = [
        'sold_quantity', 'total_revenue', 'average_rating',
        'last_sold_at', 'product__name'
    ]
    ordering = ['-sold_quantity']
