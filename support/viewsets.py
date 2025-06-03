"""
Support API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Support API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.mixins.views import PermissionByActionMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl
from core.mixins.views import FilterByTenantMixin
from core.permissions import IsOwnerOrAdmin, IsAdminUser

from .models import (
    SupportCategory, SupportTicket, TicketReply, FAQ
)
from .serializers import (
    SupportCategorySerializer, SupportTicketSerializer, 
    TicketReplySerializer, FAQSerializer, AdminSupportTicketSerializer
)


@extend_schema(tags=['Support'])
class SupportCategoryViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý SupportCategory resources.
    
    Cung cấp các endpoints để xem và quản lý danh mục hỗ trợ.
    Người dùng thường chỉ có thể xem danh mục, trong khi admin có thể thêm/sửa/xóa.
    
    Endpoints:
    - GET /api/v1/support/categories/ - Liệt kê tất cả danh mục hỗ trợ
    - POST /api/v1/support/categories/ - Tạo danh mục hỗ trợ mới (admin)
    - GET /api/v1/support/categories/{id}/ - Xem chi tiết danh mục hỗ trợ
    - PUT/PATCH /api/v1/support/categories/{id}/ - Cập nhật danh mục hỗ trợ (admin)
    - DELETE /api/v1/support/categories/{id}/ - Xóa danh mục hỗ trợ (admin)
    """
    queryset = SupportCategory.objects.all()
    serializer_class = SupportCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']
    filterset_fields = ['is_active']
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(summary="Liệt kê support tickets", tags=["Support"]),
    create=extend_schema(summary="Tạo support ticket mới", tags=["Support"]),
    retrieve=extend_schema(summary="Chi tiết support ticket", tags=["Support"]),
    update=extend_schema(summary="Cập nhật support ticket", tags=["Support"]),
    partial_update=extend_schema(summary="Cập nhật một phần support ticket", tags=["Support"]),
    destroy=extend_schema(summary="Xóa support ticket", tags=["Support"]),
)
class SupportTicketViewSet(
    StandardizedModelViewSet,
    SwaggerSchemaMixin,
    PermissionByActionMixin,
    QueryOptimizationMixin,
    FilterByTenantMixin
):
    """
    ViewSet để quản lý Support Tickets.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và quản lý support tickets.
    Users có thể xem và quản lý tickets của họ, admin có thể quản lý tất cả tickets.
    
    Endpoints:
    - GET /api/v1/support/tickets/ - Danh sách tickets của user hiện tại
    - POST /api/v1/support/tickets/ - Tạo ticket mới
    - GET /api/v1/support/tickets/{id}/ - Chi tiết ticket
    - PUT/PATCH /api/v1/support/tickets/{id}/ - Cập nhật ticket
    - DELETE /api/v1/support/tickets/{id}/ - Xóa ticket
    - POST /api/v1/support/tickets/{id}/reply/ - Trả lời ticket
    - POST /api/v1/support/tickets/{id}/close/ - Đóng ticket
    - POST /api/v1/support/tickets/{id}/reopen/ - Mở lại ticket
    """
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['subject', 'description', 'ticket_number']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    permission_classes_by_action = {
        'list': [permissions.IsAuthenticated],
        'create': [permissions.IsAuthenticated],
        'retrieve': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'update': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'partial_update': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'destroy': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'reply': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'close': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'reopen': [permissions.IsAuthenticated, IsOwnerOrAdmin],
    }

    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'create' or self.action in ['update', 'partial_update']:
            return SupportTicketSerializer
        elif self.action in ['retrieve']:
            if self.request.user.is_staff:
                return AdminSupportTicketSerializer
            return SupportTicketSerializer
        return SupportTicketSerializer
    
    def get_queryset(self):
        """Filter queryset theo user permissions."""
        queryset = SupportTicket.objects.select_related(
            'customer__user', 'category', 'assigned_to'
        ).prefetch_related('replies')

        # Non-admin users chỉ thấy tickets của họ
        if not self.request.user.is_staff:
            queryset = queryset.filter(customer__user=self.request.user)

        return queryset
    
    def perform_create(self, serializer):
        """Tự động set customer là user hiện tại."""
        # Tìm hoặc tạo customer cho user hiện tại
        from customers.models import Customer
        customer, created = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={'phone_number': '', 'address': ''}
        )
        serializer.save(customer=customer)
    
    @extend_schema(
        summary="Trả lời support ticket",
        description="Thêm reply vào support ticket",
        tags=["Support"]
    )
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Trả lời ticket."""
        ticket = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return self.error_response(
                message="Content is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Tạo reply
        reply = TicketReply.objects.create(
            ticket=ticket, 
            author=request.user,
            content=content,
            is_staff_reply=request.user.is_staff
        )
            
        # Cập nhật status nếu cần
        if ticket.status == 'closed':
            ticket.status = 'open'
            ticket.save()

        serializer = TicketReplySerializer(reply)
        return self.success_response(
            data=serializer.data,
            message="Reply added successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    @extend_schema(
        summary="Đóng support ticket",
        description="Đóng support ticket",
        tags=["Support"]
    )
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Đóng ticket."""
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()

        return self.success_response(
            message="Ticket closed successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Mở lại support ticket",
        description="Mở lại support ticket đã đóng",
        tags=["Support"]
    )
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Mở lại ticket."""
        ticket = self.get_object()
        ticket.status = 'open'
        ticket.closed_at = None
        ticket.save()

        return self.success_response(
            message="Ticket reopened successfully",
            status_code=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(summary="Liệt kê ticket replies", tags=["Support"]),
    create=extend_schema(summary="Tạo ticket reply", tags=["Support"]),
    retrieve=extend_schema(summary="Chi tiết ticket reply", tags=["Support"]),
    update=extend_schema(summary="Cập nhật ticket reply", tags=["Support"]),
    destroy=extend_schema(summary="Xóa ticket reply", tags=["Support"]),
)
class TicketReplyViewSet(
    StandardizedModelViewSet,
    SwaggerSchemaMixin,
    QueryOptimizationMixin
):
    """
    ViewSet để quản lý Ticket Replies.
    
    Cung cấp các endpoints để xem và quản lý replies của support tickets.
    """
    queryset = TicketReply.objects.all()
    serializer_class = TicketReplySerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ticket', 'is_staff_reply']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Filter queryset theo permissions."""
        queryset = TicketReply.objects.select_related('ticket__customer__user', 'author')
        
        # Non-admin users chỉ thấy replies của tickets họ sở hữu
        if not self.request.user.is_staff:
            queryset = queryset.filter(ticket__customer__user=self.request.user)
        
        return queryset


@extend_schema(tags=['Support'])
class FAQViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý FAQ resources.
    
    Cung cấp các endpoints để xem và quản lý các câu hỏi thường gặp.
    Người dùng thường chỉ có thể xem, admin có thể thêm/sửa/xóa.
    
    Endpoints:
    - GET /api/v1/support/faqs/ - Liệt kê tất cả FAQ
    - POST /api/v1/support/faqs/ - Tạo FAQ mới (admin)
    - GET /api/v1/support/faqs/{id}/ - Xem chi tiết FAQ
    - PUT/PATCH /api/v1/support/faqs/{id}/ - Cập nhật FAQ (admin)
    - DELETE /api/v1/support/faqs/{id}/ - Xóa FAQ (admin)
    - GET /api/v1/support/faqs/category/{category_id}/ - Liệt kê FAQ theo danh mục
    """
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question', 'answer']
    ordering = ['question']
    filterset_fields = ['category', 'is_published']
    
    def get_queryset(self):
        """
        Lấy danh sách FAQ. Admin xem tất cả, người dùng thường chỉ xem những FAQ đã công khai.
        """
        queryset = FAQ.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        return queryset
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        Liệt kê tất cả FAQ theo danh mục.
        """
        category = get_object_or_404(SupportCategory, id=category_id)
        
        queryset = FAQ.objects.filter(category=category)
        if not request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách FAQ cho danh mục: {category.name}",
            status_code=status.HTTP_200_OK
        )
