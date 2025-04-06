from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views.base import (
    BaseAPIView, BaseCreateView, BaseListView
)

from .models import UserToken, LoginHistory
from .serializers import (
    RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer,
    UserSessionSerializer, LoginHistorySerializer
)

User = get_user_model()


class RegisterView(BaseCreateView):
    """
    API để đăng ký tài khoản mới.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(BaseAPIView):
    """
    API để đăng xuất và vô hiệu hóa token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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


class UserDetailView(BaseAPIView):
    """
    API để lấy thông tin người dùng hiện tại.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="Thông tin người dùng",
            status_code=status.HTTP_200_OK
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API để đăng nhập và lấy JWT token.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserSessionListView(BaseListView):
    """
    API để lấy danh sách các phiên đăng nhập của người dùng hiện tại.
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_date']
    
    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user, expired_date__gt=now())


class UserSessionDeleteView(BaseAPIView):
    """
    API để đăng xuất một phiên cụ thể.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, session_id):
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
                status_code=status.HTTP_204_NO_CONTENT
            )
        except UserToken.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy phiên này",
                status_code=status.HTTP_404_NOT_FOUND
            )


class LogoutOtherSessionsView(BaseAPIView):
    """
    API để đăng xuất tất cả các phiên trừ phiên hiện tại.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        others = UserToken.objects.filter(user=request.user).exclude(token=current_token)
        
        # Cập nhật lịch sử đăng nhập
        count = others.count()
        for session in others:
            LoginHistory.objects.filter(
                user=request.user, 
                token_ref__startswith=session.token[:50]
            ).update(logout_date=now())
            
        others.delete()
        
        return self.success_response(
            message=f"Đã đăng xuất {count} thiết bị khác",
            status_code=status.HTTP_200_OK
        )


class UserLoginHistoryListView(BaseListView):
    """
    API để lấy lịch sử đăng nhập của người dùng hiện tại.
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-login_date']
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)


class TokenRefreshView(BaseAPIView):
    """
    API để refresh JWT token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return self.error_response(
                message="Token không hợp lệ hoặc đã hết hạn",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        data = serializer.validated_data
        access_token = data['access']
        refresh_token = request.data.get('refresh')

        access_obj = RefreshToken(refresh_token).access_token
        user = self._get_user_from_token(access_obj)
        expired_date = datetime.utcnow() + access_obj.lifetime

        device = request.data.get("device", "Unknown")
        ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")

        # Tạo user token mới
        UserToken.objects.create(
            user=user,
            token=str(access_token),
            expired_date=expired_date,
            device_name=device,
            ip_address=ip,
            user_agent=user_agent
        )

        # Ghi nhận lịch sử đăng nhập
        LoginHistory.objects.create(
            user=user,
            token_ref=str(access_token)[:50],
            device_name=device,
            ip_address=ip,
            user_agent=user_agent,
        )

        return self.success_response(
            data={
                "access": access_token,
                "expires_in": int(access_obj.lifetime.total_seconds()),
                "token_type": "Bearer"
            },
            message="Token đã được làm mới",
            status_code=status.HTTP_200_OK
        )

    def _get_user_from_token(self, token):
        """
        Lấy thông tin người dùng từ token.
        """
        user_id = token.get("user_id")
        return User.objects.get(id=user_id)
