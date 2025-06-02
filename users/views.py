from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.views.base import BaseAPIView
from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.permissions import IsOwnerOrAdmin, IsSellerOrAdmin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl

from .serializers import (
    UserSerializer, 
    UserDetailSerializer, 
    UserProfileSerializer,
    UserRoleUpdateSerializer,
    UserAnalyticsSerializer
)

User = get_user_model()


# =============================================================================
# LEGACY VIEWS (giữ lại để backward compatibility)
# =============================================================================

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


# =============================================================================
# NEW VIEWSETS - FULL USER MANAGEMENT
# =============================================================================

@extend_schema_view(
    list=extend_schema(summary="Liệt kê tất cả users", tags=["User Management"]),
    create=extend_schema(summary="Tạo user mới", tags=["User Management"]),
    retrieve=extend_schema(summary="Chi tiết user", tags=["User Management"]),
    update=extend_schema(summary="Cập nhật user", tags=["User Management"]),
    partial_update=extend_schema(summary="Cập nhật một phần user", tags=["User Management"]),
    destroy=extend_schema(summary="Xóa user", tags=["User Management"]),
)
class UserAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả Users.
    
    Cung cấp đầy đủ CRUD operations cho User management.
    
    Endpoints:
    - GET /api/v1/users/admin/ - Liệt kê tất cả users (admin only)
    - POST /api/v1/users/admin/ - Tạo user mới (admin only)
    - GET /api/v1/users/admin/{id}/ - Chi tiết user (admin only)
    - PUT/PATCH /api/v1/users/admin/{id}/ - Cập nhật user (admin only)
    - DELETE /api/v1/users/admin/{id}/ - Deactivate user (admin only)
    - GET /api/v1/users/admin/analytics/ - User analytics overview
    - POST /api/v1/users/admin/{id}/activate/ - Activate user
    - POST /api/v1/users/admin/{id}/deactivate/ - Deactivate user
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_seller', 'is_customer', 'is_staff', 'is_active', 'is_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['date_joined', 'last_login', 'username', 'email']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'list':
            return UserSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return UserDetailSerializer
        elif self.action == 'analytics':
            return UserAnalyticsSerializer
        return UserDetailSerializer

    def get_queryset(self):
        """Optimize queryset với prefetch."""
        queryset = User.objects.select_related().prefetch_related('groups', 'user_permissions')
        
        # Filter by role if specified
        role = self.request.query_params.get('role')
        if role == 'sellers':
            queryset = queryset.filter(is_seller=True)
        elif role == 'customers':
            queryset = queryset.filter(is_customer=True)
        elif role == 'staff':
            queryset = queryset.filter(is_staff=True)
            
        return queryset

    @extend_schema(
        summary="User analytics overview",
        description="Lấy thống kê tổng quan về users trong hệ thống",
        tags=["User Analytics"]
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Lấy analytics overview về users."""
        
        # Basic counts
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        seller_users = User.objects.filter(is_seller=True).count()
        customer_users = User.objects.filter(is_customer=True).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        # Active users (logged in last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recently_active = User.objects.filter(last_login__gte=seven_days_ago).count()
        
        # Registration trend (last 12 months)
        registration_trend = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            if i < 11:
                month_end = timezone.now().replace(day=1) - timedelta(days=30*(i-1))
            else:
                month_end = timezone.now()
            
            count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            registration_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        analytics_data = {
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'seller_users': seller_users,
            'customer_users': customer_users,
            'recent_registrations': recent_registrations,
            'recently_active': recently_active,
            'registration_trend': list(reversed(registration_trend)),
            'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
            'activity_rate': round((recently_active / total_users * 100), 2) if total_users > 0 else 0,
        }
        
        return self.success_response(
            data=analytics_data,
            message="User analytics retrieved successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Activate user account",
        description="Kích hoạt tài khoản user",
        tags=["User Management"]
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Kích hoạt user account."""
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        return self.success_response(
            data={'is_active': True},
            message=f"User {user.username} đã được kích hoạt",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Deactivate user account", 
        description="Vô hiệu hóa tài khoản user",
        tags=["User Management"]
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Vô hiệu hóa user account."""
        user = self.get_object()
        
        # Không cho phép deactivate superuser
        if user.is_superuser:
            return self.error_response(
                message="Không thể vô hiệu hóa superuser",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        return self.success_response(
            data={'is_active': False},
            message=f"User {user.username} đã được vô hiệu hóa",
            status_code=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(summary="Lấy thông tin profile hiện tại", tags=["User Self Management"]),
    update=extend_schema(summary="Cập nhật profile", tags=["User Self Management"]),
    partial_update=extend_schema(summary="Cập nhật một phần profile", tags=["User Self Management"]),
)
class UserSelfViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để user quản lý profile của chính mình.
    
    Cung cấp các endpoints để user tự quản lý thông tin cá nhân.
    
    Endpoints:
    - GET /api/v1/users/me/ - Lấy thông tin profile hiện tại
    - PUT/PATCH /api/v1/users/me/ - Cập nhật profile
    - POST /api/v1/users/me/upload-avatar/ - Upload avatar
    - POST /api/v1/users/me/change-password/ - Đổi mật khẩu
    - GET /api/v1/users/me/activity/ - Lịch sử hoạt động
    - GET /api/v1/users/me/settings/ - Cài đặt cá nhân
    - PUT /api/v1/users/me/settings/ - Cập nhật cài đặt
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head', 'options']

    def get_queryset(self):
        """Chỉ trả về user hiện tại."""
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        """Lấy user hiện tại."""
        return self.request.user

    def list(self, request, *args, **kwargs):
        """Lấy thông tin profile hiện tại."""
        serializer = self.get_serializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="Profile information retrieved successfully",
            status_code=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        """Cập nhật profile."""
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Profile updated successfully",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Profile update failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def partial_update(self, request, *args, **kwargs):
        """Cập nhật một phần profile."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="Upload avatar",
        description="Upload avatar cho user hiện tại",
        tags=["User Self Management"]
    )
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """Upload avatar."""
        if 'avatar' not in request.FILES:
            return self.error_response(
                message="No avatar file provided",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save(update_fields=['avatar'])
        
        return self.success_response(
            data={'avatar': user.avatar.url if user.avatar else None},
            message="Avatar uploaded successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Change password",
        description="Đổi mật khẩu cho user hiện tại",
        tags=["User Self Management"]
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Đổi mật khẩu."""
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return self.error_response(
                message="Current password and new password are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        
        # Kiểm tra mật khẩu hiện tại
        if not user.check_password(current_password):
            return self.error_response(
                message="Current password is incorrect",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Set mật khẩu mới
        user.set_password(new_password)
        user.save()
        
        return self.success_response(
            message="Password changed successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="User activity log",
        description="Lấy lịch sử hoạt động của user",
        tags=["User Self Management"]
    )
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """Lấy lịch sử hoạt động."""
        user = request.user
        
        # Tạm thời trả về thông tin cơ bản
        # Sau này có thể mở rộng với activity logging system
        activity_data = {
            'last_login': user.last_login,
            'last_login_ip': user.last_login_ip,
            'date_joined': user.date_joined,
            'login_count': 0,  # Cần implement tracking
            'profile_updates': 0,  # Cần implement tracking
        }
        
        return self.success_response(
            data=activity_data,
            message="User activity retrieved successfully",
            status_code=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(summary="Liệt kê user roles", tags=["User Role Management"]),
    update=extend_schema(summary="Cập nhật user roles", tags=["User Role Management"]),
)
class UserRoleViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý roles của users.
    
    Chỉ admin mới có thể quản lý roles.
    
    Endpoints:
    - GET /api/v1/users/roles/{user_id}/ - Lấy roles của user
    - PUT/PATCH /api/v1/users/roles/{user_id}/ - Cập nhật roles
    - GET /api/v1/users/roles/sellers/ - Liệt kê sellers
    - GET /api/v1/users/roles/customers/ - Liệt kê customers
    - GET /api/v1/users/roles/staff/ - Liệt kê staff
    """
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_serializer_class(self):
        """Trả về serializer phù hợp."""
        if self.action in ['list', 'retrieve']:
            return UserSerializer
        return UserRoleUpdateSerializer

    def update(self, request, *args, **kwargs):
        """Cập nhật roles của user."""
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=UserSerializer(user).data,
                message=f"Roles updated for user {user.username}",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Role update failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Liệt kê sellers",
        description="Lấy danh sách tất cả sellers",
        tags=["User Role Management"]
    )
    @action(detail=False, methods=['get'])
    def sellers(self, request):
        """Lấy danh sách sellers."""
        sellers = User.objects.filter(is_seller=True)
        serializer = UserSerializer(sellers, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Sellers retrieved successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Liệt kê customers",
        description="Lấy danh sách tất cả customers", 
        tags=["User Role Management"]
    )
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """Lấy danh sách customers."""
        customers = User.objects.filter(is_customer=True)
        serializer = UserSerializer(customers, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Customers retrieved successfully",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Liệt kê staff",
        description="Lấy danh sách tất cả staff",
        tags=["User Role Management"]
    )
    @action(detail=False, methods=['get'])
    def staff(self, request):
        """Lấy danh sách staff."""
        staff = User.objects.filter(is_staff=True)
        serializer = UserSerializer(staff, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Staff retrieved successfully",
            status_code=status.HTTP_200_OK
        )
