"""
Traffic Log views module
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from ..models import TrafficLog
from ..serializers import TrafficLogSerializer


class TrafficLogListView(generics.ListAPIView):
    """
    API view để liệt kê nhật ký lưu lượng truy cập.
    
    GET /reports/traffic - Liệt kê nhật ký lưu lượng
    
    Chỉ admin mới có thể truy cập.
    Hỗ trợ tìm kiếm, lọc và sắp xếp theo nhiều tiêu chí.
    """
    queryset = TrafficLog.objects.all()
    serializer_class = TrafficLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'endpoint']
    search_fields = ['endpoint', 'ip_address']
    ordering_fields = ['timestamp', 'duration_ms']
    ordering = ['-timestamp']
