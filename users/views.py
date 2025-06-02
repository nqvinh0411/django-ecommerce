from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny

from core.views.base import BaseAPIView
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl

from .serializers import UserSerializer, UserDetailSerializer

User = get_user_model()


class UserDetailView(BaseAPIView):
    """
    API để lấy thông tin người dùng hiện tại.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="Thông tin người dùng",
            status_code=status.HTTP_200_OK
        )


class UserProfileUpdateView(BaseAPIView):
    """
    API để cập nhật thông tin profile của user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailSerializer

    def patch(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        
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
