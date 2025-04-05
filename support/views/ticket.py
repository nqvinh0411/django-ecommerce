"""
Support Ticket views module
"""
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import SupportTicket
from ..serializers import SupportTicketSerializer, TicketReplySerializer
from ..permissions import IsOwnerOrAdmin


class SupportTicketListCreateView(generics.ListCreateAPIView):
    """
    API view để liệt kê tất cả các ticket của khách hàng đã xác thực hoặc tạo ticket mới.
    
    GET /support/tickets - Liệt kê ticket hỗ trợ
    POST /support/tickets - Tạo ticket hỗ trợ mới
    
    Người dùng đã xác thực có thể tạo và xem ticket của họ.
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Regular users can only see their own tickets
        if not self.request.user.is_staff:
            return SupportTicket.objects.filter(customer__user=self.request.user)
        # Staff can see all tickets
        return SupportTicket.objects.all()


class SupportTicketRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    API view để xem hoặc cập nhật một ticket cụ thể.
    
    GET /support/tickets/{ticket_id} - Xem chi tiết ticket
    PUT/PATCH /support/tickets/{ticket_id} - Cập nhật ticket
    
    Người dùng chỉ có thể xem và cập nhật ticket của họ.
    Chỉ nhân viên mới có thể cập nhật trạng thái.
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_url_kwarg = 'ticket_id'

    def get_queryset(self):
        if not self.request.user.is_staff:
            return SupportTicket.objects.filter(customer__user=self.request.user)
        return SupportTicket.objects.all()
    
    def update(self, request, *args, **kwargs):
        # Only staff can update status
        if 'status' in request.data and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to update ticket status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class TicketReplyCreateView(generics.CreateAPIView):
    """
    API view để tạo phản hồi cho một ticket cụ thể.
    
    POST /support/tickets/{ticket_id}/reply - Tạo phản hồi mới
    
    Người dùng chỉ có thể tạo phản hồi trên ticket của họ.
    Nhân viên có thể tạo phản hồi trên bất kỳ ticket nào.
    """
    serializer_class = TicketReplySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        
        # Check permissions
        if not self.request.user.is_staff and ticket.customer.user != self.request.user:
            self.permission_denied(self.request)
            
        # Create the reply
        serializer.save(ticket=ticket, user=self.request.user, is_staff_reply=self.request.user.is_staff)
        
        # Update ticket status when staff replies
        if self.request.user.is_staff and ticket.status == 'pending':
            ticket.status = 'in_progress'
            ticket.save(update_fields=['status'])
