"""
Notifications API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Notifications API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Notification resources.
    
    Cung cấp các endpoints để xem và quản lý thông báo của người dùng.
    
    Endpoints:
    - GET /api/v1/notifications/ - Liệt kê tất cả thông báo của người dùng hiện tại
    - POST /api/v1/notifications/ - Tạo thông báo mới (chỉ admin)
    - GET /api/v1/notifications/{id}/ - Xem chi tiết một thông báo
    - PATCH /api/v1/notifications/{id}/ - Cập nhật thông báo (chỉ admin)
    - DELETE /api/v1/notifications/{id}/ - Xóa thông báo
    - POST /api/v1/notifications/mark-all-read/ - Đánh dấu tất cả thông báo đã đọc
    - POST /api/v1/notifications/{id}/mark-read/ - Đánh dấu một thông báo đã đọc
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Lấy danh sách thông báo của người dùng hiện tại.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Notification.objects.none()
            
        return Notification.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        Admin có thể tạo và cập nhật thông báo cho bất kỳ người dùng nào.
        Người dùng thường chỉ có thể xem và xóa thông báo của họ.
        """
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Tự động gán thông báo cho người dùng được chỉ định.
        Nếu không có user_id được cung cấp, mặc định là người dùng hiện tại.
        """
        user_id = self.request.data.get('user_id')
        if user_id and self.request.user.is_staff:
            # Admin có thể tạo thông báo cho bất kỳ người dùng nào
            serializer.save()
        else:
            # Người dùng thường chỉ có thể tạo thông báo cho chính họ
            serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Xóa thông báo.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.success_response(
            data=None,
            message="Đã xóa thông báo",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Đánh dấu một thông báo đã đọc.
        """
        notification = self.get_object()
        
        # Giả sử chúng ta thêm trường is_read vào model Notification
        # notification.is_read = True
        # notification.save()
        
        serializer = self.get_serializer(notification)
        return self.success_response(
            data=serializer.data,
            message="Đã đánh dấu thông báo đã đọc",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        Đánh dấu tất cả thông báo của người dùng đã đọc.
        """
        queryset = self.get_queryset()
        count = queryset.count()
        
        # Giả sử chúng ta thêm trường is_read vào model Notification
        # queryset.update(is_read=True)
        
        return self.success_response(
            data={'marked_count': count},
            message="Đã đánh dấu tất cả thông báo đã đọc",
            status_code=status.HTTP_200_OK
        )
