from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import SupportTicket, TicketReply, FAQ, SupportCategory
from .serializers import (
    SupportTicketSerializer, 
    TicketReplySerializer, 
    FAQSerializer,
    AdminSupportTicketSerializer,
    SupportCategorySerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser


class SupportCategoryListView(generics.ListAPIView):
    """
    List all active support categories
    """
    queryset = SupportCategory.objects.filter(is_active=True)
    serializer_class = SupportCategorySerializer
    permission_classes = [AllowAny]


class SupportTicketListCreateView(generics.ListCreateAPIView):
    """
    List all tickets for the authenticated customer or create a new ticket
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


class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a specific ticket
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
    Create a reply for a specific ticket
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


class AdminSupportTicketListView(generics.ListAPIView):
    """
    Admin view to list all support tickets
    """
    queryset = SupportTicket.objects.all()
    serializer_class = AdminSupportTicketSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'customer__user__email', 'customer__user__username']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = SupportTicket.objects.all()
        
        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset


class FAQListView(generics.ListAPIView):
    """
    Public view to list all published FAQs
    """
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_published=True)
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset
