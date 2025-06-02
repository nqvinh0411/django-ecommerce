from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from drf_spectacular.utils import extend_schema

from core.viewsets.base import StandardizedModelViewSet
from .backends import EmailBackend
from .models import UserToken, LoginHistory
from .serializers import (
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    UserTokenSerializer, LoginHistorySerializer, LogoutSerializer
)

User = get_user_model()


@extend_schema(tags=['Authentication'])
class AuthViewSet(StandardizedModelViewSet):
    """
    ViewSet để xử lý Authentication.
    
    Endpoints:
    - POST /api/v1/auth/register/ - Đăng ký tài khoản mới
    - POST /api/v1/auth/login/ - Đăng nhập
    - POST /api/v1/auth/logout/ - Đăng xuất
    - POST /api/v1/auth/logout-all/ - Đăng xuất tất cả thiết bị
    - POST /api/v1/auth/token/refresh/ - Refresh JWT token
    - POST /api/v1/auth/change-password/ - Đổi mật khẩu
    - GET /api/v1/auth/sessions/ - Lấy danh sách phiên đăng nhập
    - DELETE /api/v1/auth/sessions/{id}/ - Xóa phiên đăng nhập
    - GET /api/v1/auth/login-history/ - Lịch sử đăng nhập
    """
    queryset = User.objects.none()  # Không cần queryset cho auth
    serializer_class = LoginSerializer  # Default serializer for Swagger
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        action_serializers = {
            'register': RegisterSerializer,
            'login': LoginSerializer,
            'logout': LogoutSerializer,
            'logout_all': LogoutSerializer,
            'token_refresh': TokenRefreshSerializer,
            'change_password': ChangePasswordSerializer,
            'sessions': UserTokenSerializer,
            'delete_session': UserTokenSerializer,
            'login_history': LoginHistorySerializer,
        }
        
        return action_serializers.get(self.action, self.serializer_class)

    def get_permissions(self):
        if self.action in ['register', 'login', 'token_refresh']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """Đăng ký tài khoản mới."""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Tạo JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            return self.success_response(
                data={
                    'access': str(access),
                    'refresh': str(refresh),
                    'expires_in': int(access.lifetime.total_seconds()),
                    'token_type': 'Bearer',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                },
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
        """Đăng nhập bằng email và mật khẩu."""
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        device = serializer.validated_data['device']

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
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            },
            message="Đăng nhập thành công",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='logout')
    def logout(self, request):
        """Đăng xuất và vô hiệu hóa token."""
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
                message="Đăng xuất thất bại",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='logout-all')
    def logout_all(self, request):
        """Đăng xuất tất cả thiết bị."""
        try:
            # Xóa tất cả tokens của user
            UserToken.objects.filter(user=request.user).delete()
            
            # Cập nhật lịch sử đăng nhập
            LoginHistory.objects.filter(
                user=request.user,
                logout_date__isnull=True
            ).update(logout_date=now())
            
            return self.success_response(
                message="Đăng xuất tất cả thiết bị thành công",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message="Đăng xuất thất bại",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='token/refresh')
    def token_refresh(self, request):
        """Refresh JWT token."""
        serializer = TokenRefreshSerializer(data=request.data)
        
        if serializer.is_valid():
            return self.success_response(
                data=serializer.validated_data,
                message="Token được làm mới thành công",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Làm mới token thất bại",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='change-password')
    def change_password(self, request):
        """Đổi mật khẩu."""
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Kiểm tra mật khẩu hiện tại
            if not user.check_password(serializer.validated_data['current_password']):
                return self.error_response(
                    message="Mật khẩu hiện tại không đúng",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Đổi mật khẩu
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return self.success_response(
                message="Đổi mật khẩu thành công",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Đổi mật khẩu thất bại",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='sessions')
    def sessions(self, request):
        """Lấy danh sách các phiên đăng nhập."""
        tokens = UserToken.objects.filter(user=request.user).order_by('-created_date')
        serializer = UserTokenSerializer(tokens, many=True, context={'request': request})
        
        return self.success_response(
            data=serializer.data,
            message="Lấy danh sách phiên đăng nhập thành công",
            status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated], url_path='sessions')
    def delete_session(self, request, pk=None):
        """Xóa một phiên đăng nhập cụ thể."""
        try:
            token = UserToken.objects.get(id=pk, user=request.user)
            token.delete()
            
            # Cập nhật lịch sử
            LoginHistory.objects.filter(
                user=request.user,
                token_ref__startswith=token.token[:50]
            ).update(logout_date=now())
            
            return self.success_response(
                message="Xóa phiên đăng nhập thành công",
                status_code=status.HTTP_200_OK
            )
        except UserToken.DoesNotExist:
            return self.error_response(
                message="Phiên đăng nhập không tồn tại",
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='login-history')
    def login_history(self, request):
        """Lấy lịch sử đăng nhập."""
        histories = LoginHistory.objects.filter(user=request.user).order_by('-login_date')
        
        # Phân trang
        page = self.paginate_queryset(histories)
        if page is not None:
            serializer = LoginHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LoginHistorySerializer(histories, many=True)
        return self.success_response(
            data=serializer.data,
            message="Lấy lịch sử đăng nhập thành công",
            status_code=status.HTTP_200_OK
        ) 