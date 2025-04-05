"""
Usage Log views module
"""
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from core.views.base import BaseListView
from ..models import UsageLog
from ..serializers import UsageLogSerializer


class UsageLogListView(BaseListView):
    """
    API để liệt kê lịch sử sử dụng khuyến mãi.
    GET /promotions/usage-logs
    
    Admin có thể xem tất cả log, khách hàng chỉ xem được log của họ.
    """
    serializer_class = UsageLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['promo_type']
    ordering_fields = ['used_at']
    ordering = ['-used_at']
    
    def get_queryset(self):
        """
        Return all logs for admin, or only the user's logs for customers.
        """
        queryset = UsageLog.objects.all()
        
        if not self.request.user.is_staff:
            # Non-staff users can only see their own logs
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
