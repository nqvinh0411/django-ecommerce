"""
Users API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Users API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.optimization.mixins import QueryOptimizationMixin
from drf_spectacular.utils import extend_schema

from .serializers import UserSerializer

User = get_user_model()


@extend_schema(tags=['Users'])
class UserViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý User profile và preferences.
    
    Endpoints:
    - GET /api/v1/users/me/ - Lấy thông tin người dùng hiện tại
    - PUT /api/v1/users/me/ - Cập nhật thông tin người dùng
    - PATCH /api/v1/users/me/ - Cập nhật một phần thông tin người dùng
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='me')
    def me(self, request):
        """Lấy thông tin người dùng hiện tại."""
        serializer = UserSerializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="Lấy thông tin người dùng thành công",
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated], url_path='me')
    def update_me(self, request):
        """Cập nhật thông tin người dùng hiện tại."""
        serializer = UserSerializer(request.user, data=request.data, partial=request.method == 'PATCH')
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Cập nhật thông tin thành công",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Cập nhật thông tin thất bại",
            status_code=status.HTTP_400_BAD_REQUEST
        )
