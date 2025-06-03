"""
Admin Support views module
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from ..models import SupportTicket
from ..serializers import AdminSupportTicketSerializer
from core.permissions import IsAdminUser


class AdminSupportTicketListView(generics.ListAPIView):
    """
    API view dành cho admin để liệt kê tất cả các ticket hỗ trợ.
    
    GET /support/admin/tickets - Liệt kê tất cả ticket hỗ trợ (dành cho admin)
    
    Chỉ dành cho admin. Hỗ trợ tìm kiếm và sắp xếp.
    """
    queryset = SupportTicket.objects.all()
    serializer_class = AdminSupportTicketSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'customer__user__email', 'customer__user__username']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Lọc danh sách ticket theo trạng thái (nếu được cung cấp trong query params).
        """
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
