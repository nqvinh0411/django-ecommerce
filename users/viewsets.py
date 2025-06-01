"""
Users API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Users API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import permissions, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.optimization.mixins import QueryOptimizationMixin
from users.backends import EmailBackend
from drf_spectacular.utils import extend_schema

from .models import UserToken, LoginHistory
from .serializers import (
    RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer,
    UserSessionSerializer, LoginHistorySerializer
)

User = get_user_model()


@extend_schema(tags=['Authentication'])
class UserViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý User resources.
    
    Cung cấp các endpoints để đăng ký, đăng nhập, đăng xuất và quản lý thông tin người dùng.
    
    Endpoints:
    - POST /api/v1/users/register/ - Đăng ký tài khoản mới
    - POST /api/v1/users/login/ - Đăng nhập và lấy JWT token
    - POST /api/v1/users/logout/ - Đăng xuất và vô hiệu hóa token
    - POST /api/v1/users/token/refresh/ - Refresh JWT token
    - GET /api/v1/users/me/ - Lấy thông tin người dùng hiện tại
    - GET /api/v1/users/sessions/ - Lấy danh sách các phiên đăng nhập
    - DELETE /api/v1/users/sessions/{id}/ - Đăng xuất một phiên cụ thể
    - POST /api/v1/users/sessions/logout-others/ - Đăng xuất tất cả các phiên khác
    - GET /api/v1/users/login-history/ - Lấy lịch sử đăng nhập
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['register', 'login', 'token_refresh']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Trả về lớp serializer phù hợp cho từng hành động.
        """
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'sessions':
            return UserSessionSerializer
        elif self.action == 'login_history':
            return LoginHistorySerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Đăng ký tài khoản mới.
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)
            
            return self.success_response(
                data=user_serializer.data,
                message="Đăng ký tài khoản thành công",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Đăng ký tài khoản thất bại",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Đăng nhập bằng email và mật khẩu, trả về JWT tokens.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        device = request.data.get('device', 'Unknown')

        if not email or not password:
            return self.error_response(
                message="Email và mật khẩu là bắt buộc",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        backend = EmailBackend()
        user = backend.authenticate(request, email=email, password=password)
        
        if not user:
            return self.error_response(
                message="Email hoặc mật khẩu không chính xác",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # Tạo JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Lưu token & lịch sử đăng nhập
        expired_date = timezone.now() + access.lifetime
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        UserToken.objects.create(
            user=user,
            token=str(access),
            expired_date=expired_date,
            device_name=device,
            ip_address=ip,
            user_agent=user_agent,
        )

        LoginHistory.objects.create(
            user=user,
            token_ref=str(access)[:50],
            device_name=device,
            ip_address=ip,
            user_agent=user_agent,
        )

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return self.success_response(
            data={
                'access': str(access),
                'refresh': str(refresh),
                'expires_in': int(access.lifetime.total_seconds()),
                'token_type': 'Bearer',
                'user': UserSerializer(user).data,
            },
            message="Đăng nhập thành công",
            status_code=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='logout')
    def logout(self, request):
        """
        Đăng xuất và vô hiệu hóa token.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return self.error_response(
                    message="Refresh token không được cung cấp",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Cập nhật lịch sử đăng nhập
            current_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
            try:
                user_token = UserToken.objects.get(token=current_token)
                user_token.delete()
                
                LoginHistory.objects.filter(
                    user=request.user, 
                    token_ref__startswith=current_token[:50]
                ).update(logout_date=now())
            except UserToken.DoesNotExist:
                pass
                
            return self.success_response(
                message="Đăng xuất thành công",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message=f"Token không hợp lệ: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='token/refresh')
    def token_refresh(self, request):
        """
        Refresh JWT token.
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.error_response(
                message="Refresh token không được cung cấp",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            token = RefreshToken(refresh_token)
            
            # Lấy thông tin người dùng
            user_id = token.payload.get('user_id')
            user = User.objects.filter(id=user_id).first()
            
            if not user:
                return self.error_response(
                    message="Không tìm thấy người dùng",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Tạo token mới
            access_token = str(token.access_token)
            
            return self.success_response(
                data={
                    'access': access_token,
                    'refresh': str(token),
                    'token_type': 'Bearer',
                },
                message="Token đã được làm mới",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message=f"Token không hợp lệ: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='me')
    def me(self, request):
        """
        Lấy thông tin người dùng hiện tại.
        """
        serializer = UserSerializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="Thông tin người dùng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='sessions')
    def sessions(self, request):
        """
        Lấy danh sách các phiên đăng nhập của người dùng hiện tại.
        """
        queryset = UserToken.objects.filter(user=request.user, expired_date__gt=now()).order_by('-created_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSessionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSessionSerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách phiên đăng nhập",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated], url_path='sessions/(?P<session_id>[^/.]+)')
    def delete_session(self, request, pk=None, session_id=None):
        """
        Đăng xuất một phiên cụ thể.
        """
        try:
            session = UserToken.objects.get(pk=session_id, user=request.user)
            
            # Cập nhật lịch sử đăng nhập
            LoginHistory.objects.filter(
                user=request.user, 
                token_ref__startswith=session.token[:50]
            ).update(logout_date=now())
            
            session.delete()
            
            return self.success_response(
                message="Đã đăng xuất phiên này",
                status_code=status.HTTP_200_OK
            )
        except UserToken.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy phiên này",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='sessions/logout-others')
    def logout_other_sessions(self, request):
        """
        Đăng xuất tất cả các phiên khác ngoại trừ phiên hiện tại.
        """
        current_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        
        # Cập nhật lịch sử đăng nhập
        sessions = UserToken.objects.filter(user=request.user).exclude(token=current_token)
        
        if sessions.exists():
            for session in sessions:
                LoginHistory.objects.filter(
                    user=request.user, 
                    token_ref__startswith=session.token[:50]
                ).update(logout_date=now())
            
            sessions_count = sessions.count()
            sessions.delete()
            
            return self.success_response(
                data={"sessions_ended": sessions_count},
                message="Đã đăng xuất tất cả các phiên khác",
                status_code=status.HTTP_200_OK
            )
        
        return self.success_response(
            message="Không có phiên nào khác để đăng xuất",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='login-history')
    def login_history(self, request):
        """
        Lấy lịch sử đăng nhập của người dùng hiện tại.
        """
        queryset = LoginHistory.objects.filter(user=request.user).order_by('-login_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LoginHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LoginHistorySerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Lịch sử đăng nhập",
            status_code=status.HTTP_200_OK
        )
