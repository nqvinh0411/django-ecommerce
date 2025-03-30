from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime
from .models import UserToken

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

        user = self.user
        refresh = self.get_token(user)
        access_token = refresh.access_token

        expires_in = int(access_token.lifetime.total_seconds())

        # Lưu UserToken như trước...
        expired_date = datetime.utcnow() + access_token.lifetime
        UserToken.objects.create(
            user=user,
            token=str(access_token),
            expired_date=expired_date
        )

        return {
            'refresh': str(refresh),
            'access': str(access_token),
            'expires_in': expires_in,
            'token_type': 'Bearer',
        }
