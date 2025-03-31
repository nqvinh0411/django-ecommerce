from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserToken, LoginHistory
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


# API Đăng ký
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# API Đăng nhập (sử dụng JWT mặc định của DRF SimpleJWT)


# API Đăng xuất
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)


# API Lấy thông tin người dùng hiện tại
class UserDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token = data['access']
        refresh_token = data['refresh']
        user = self.user

        access = self.get_token(user).access_token
        expired_date = datetime.utcnow() + access.lifetime

        request = self.context['request']
        device = request.data.get('device', 'Unknown')
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        # Tạo UserToken
        UserToken.objects.create(
            user=user,
            token=str(access_token),
            expired_date=expired_date,
            device_name=device,
            ip_address=ip,
            user_agent=user_agent
        )

        # Ghi log login
        LoginHistory.objects.create(
            user=user,
            token_ref=str(access_token)[:50],
            device_name=device,
            ip_address=ip,
            user_agent=user_agent,
        )

        return {
            'access': access_token,
            'refresh': refresh_token,
            'expires_in': int(access.lifetime.total_seconds()),
            'token_type': 'Bearer'
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserSessionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = UserToken.objects.filter(user=request.user, expired_date__gt=now())
        data = [
            {
                "id": s.id,
                "device": s.device_name,
                "ip": s.ip_address,
                "user_agent": s.user_agent,
                "created": s.created_date,
                "expires": s.expired_date,
            }
            for s in sessions
        ]
        return Response(data)


class UserSessionDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            session = UserToken.objects.get(pk=pk, user=request.user)
            LoginHistory.objects.filter(
                user=request.user, token_ref__startswith=session.token[:50]
            ).update(logout_date=now())
            session.delete()
            return Response({"message": "Đã đăng xuất phiên này."}, status=204)
        except UserToken.DoesNotExist:
            return Response({"error": "Không tìm thấy phiên này."}, status=404)


class LogoutOtherSessionsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        others = UserToken.objects.filter(user=request.user).exclude(token=current_token)
        for session in others:
            LoginHistory.objects.filter(
                user=request.user, token_ref__startswith=session.token[:50]
            ).update(logout_date=now())
        count = others.count()
        others.delete()
        return Response({"message": "Đã đăng xuất {} thiết bị khác.".format(count)})


class UserLoginHistoryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        histories = LoginHistory.objects.filter(user=request.user).order_by('-login_date')
        data = [
            {
                "device": h.device_name,
                "ip": h.ip_address,
                "login": h.login_date,
                "logout": h.logout_date,
                "user_agent": h.user_agent,
            } for h in histories
        ]
        return Response(data)
