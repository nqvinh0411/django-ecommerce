"""
Support API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Support API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from customers.models import Customer
from .models import SupportCategory, SupportTicket, TicketReply, FAQ
from .serializers import (
    SupportCategorySerializer, SupportTicketSerializer, 
    TicketReplySerializer, FAQSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser


class SupportCategoryViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
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


class SupportTicketViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý SupportTicket resources.
    
    Cung cấp các endpoints để xem và quản lý ticket hỗ trợ.
    Người dùng thường chỉ có thể xem và tạo ticket của họ, 
    trong khi admin có thể xem tất cả ticket.
    
    Endpoints:
    - GET /api/v1/support/tickets/ - Liệt kê tất cả ticket của người dùng (admin xem tất cả)
    - POST /api/v1/support/tickets/ - Tạo ticket mới
    - GET /api/v1/support/tickets/{id}/ - Xem chi tiết ticket
    - PUT/PATCH /api/v1/support/tickets/{id}/ - Cập nhật ticket (chỉ người tạo hoặc admin)
    - DELETE /api/v1/support/tickets/{id}/ - Xóa ticket (chỉ admin)
    - POST /api/v1/support/tickets/{id}/reply/ - Trả lời ticket
    - GET /api/v1/support/tickets/admin/ - Admin xem danh sách tất cả ticket (chỉ admin)
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'message', 'customer__user__email']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    filterset_fields = ['status', 'category']
    
    def get_queryset(self):
        """
        Lấy danh sách ticket. Admin xem tất cả, người dùng thường chỉ xem ticket của họ.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return SupportTicket.objects.none()
            
        if self.request.user.is_staff:
            return SupportTicket.objects.all()
        
        customer = get_object_or_404(Customer, user=self.request.user)
        return SupportTicket.objects.filter(customer=customer)
    
    def perform_create(self, serializer):
        """
        Tạo ticket mới, tự động gán cho customer hiện tại.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        serializer.save(customer=customer)
    
    @action(detail=True, methods=['post'], url_path='reply')
    def reply(self, request, pk=None):
        """
        Trả lời một ticket.
        """
        ticket = self.get_object()
        serializer = TicketReplySerializer(data=request.data)
        
        if serializer.is_valid():
            # Xác định xem đây có phải là reply từ nhân viên không
            is_staff_reply = request.user.is_staff
            
            reply = serializer.save(
                ticket=ticket, 
                user=request.user,
                is_staff_reply=is_staff_reply
            )
            
            # Cập nhật trạng thái ticket nếu cần
            if is_staff_reply and ticket.status == 'pending':
                ticket.status = 'in_progress'
                ticket.save(update_fields=['status', 'updated_at'])
            
            return self.success_response(
                data=serializer.data,
                message="Đã thêm phản hồi vào ticket",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Dữ liệu không hợp lệ",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], url_path='admin', permission_classes=[permissions.IsAdminUser])
    def admin_list(self, request):
        """
        Liệt kê tất cả ticket cho admin với thông tin bổ sung.
        """
        queryset = SupportTicket.objects.all()
        
        # Áp dụng filter, search, ordering
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách tất cả ticket hỗ trợ",
            status_code=status.HTTP_200_OK
        )


class TicketReplyViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý TicketReply resources.
    
    Cung cấp các endpoints để xem và quản lý phản hồi cho ticket.
    
    Endpoints:
    - GET /api/v1/support/replies/ - Liệt kê tất cả phản hồi (admin)
    - GET /api/v1/support/replies/{id}/ - Xem chi tiết phản hồi
    - DELETE /api/v1/support/replies/{id}/ - Xóa phản hồi (chỉ người tạo hoặc admin)
    - GET /api/v1/support/replies/ticket/{ticket_id}/ - Liệt kê phản hồi cho một ticket cụ thể
    """
    serializer_class = TicketReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']
    filterset_fields = ['is_staff_reply', 'ticket']
    
    def get_queryset(self):
        """
        Lấy danh sách phản hồi mà người dùng có quyền xem.
        Admin xem tất cả, người dùng thường chỉ xem phản hồi trong ticket của họ.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return TicketReply.objects.none()
            
        if self.request.user.is_staff:
            return TicketReply.objects.all()
        
        customer = get_object_or_404(Customer, user=self.request.user)
        return TicketReply.objects.filter(ticket__customer=customer)
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], url_path='ticket/(?P<ticket_id>[^/.]+)')
    def by_ticket(self, request, ticket_id=None):
        """
        Liệt kê tất cả phản hồi cho một ticket cụ thể.
        """
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        
        # Kiểm tra quyền truy cập
        if not request.user.is_staff and ticket.customer.user != request.user:
            return self.error_response(
                message="Bạn không có quyền xem phản hồi của ticket này",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        replies = TicketReply.objects.filter(ticket=ticket).order_by('created_at')
        serializer = self.get_serializer(replies, many=True)
        
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách phản hồi cho ticket #{ticket_id}",
            status_code=status.HTTP_200_OK
        )


class FAQViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
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
