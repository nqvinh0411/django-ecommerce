from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.validators.common import validate_password

from .models import UserToken, LoginHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer cho model User, hiển thị thông tin người dùng.
    """
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_seller', 'is_customer', 'phone_number', 'address',
            'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc đăng ký người dùng mới.
    """
    password = serializers.CharField(
        style={'input_type': 'password'},
        required=True,
        write_only=True
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        required=True,
        write_only=True
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'is_seller', 'is_customer'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'is_seller': {'required': False, 'default': False},
            'is_customer': {'required': False, 'default': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng")
        return value
        
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập này đã được sử dụng")
        return value
        
    def validate_password(self, value):
        return validate_password(value)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Mật khẩu xác nhận không khớp'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc cập nhật thông tin người dùng.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'address')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer cho việc thay đổi mật khẩu.
    """
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu hiện tại không đúng")
        return value
        
    def validate_new_password(self, value):
        return validate_password(value)
        
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Mật khẩu xác nhận không khớp'})
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer cho UserToken, hiển thị thông tin phiên đăng nhập.
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    created_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    expired_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    is_current = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserToken
        fields = (
            'id', 'user_id', 'username', 'device_name', 'ip_address',
            'user_agent', 'created_date', 'expired_date', 'is_current'
        )
        read_only_fields = fields
    
    def get_is_current(self, obj):
        request = self.context.get('request')
        if request:
            current_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
            return obj.token == current_token
        return False


class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer cho LoginHistory, hiển thị lịch sử đăng nhập.
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    login_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    logout_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    session_duration = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LoginHistory
        fields = (
            'id', 'user_id', 'username', 'device_name', 'ip_address',
            'user_agent', 'login_date', 'logout_date', 'session_duration'
        )
        read_only_fields = fields
    
    def get_session_duration(self, obj):
        if obj.logout_date and obj.login_date:
            duration = obj.logout_date - obj.login_date
            return int(duration.total_seconds())
        return None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer cho việc đăng nhập và lấy JWT token.
    """
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

        # Cập nhật last_login
        user.last_login = datetime.now()
        user.save(update_fields=['last_login'])

        return {
            'access': access_token,
            'refresh': refresh_token,
            'expires_in': int(access.lifetime.total_seconds()),
            'token_type': 'Bearer',
            'user': UserSerializer(user).data
        }
