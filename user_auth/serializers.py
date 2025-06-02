from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema_field

from .models import UserToken, UserSession, LoginHistory, PasswordResetToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer để đăng ký user mới.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm',
            'is_seller', 'is_customer'
        ]
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Mật khẩu xác nhận không khớp'
            })
        return data
    
    def validate_email(self, value):
        """Check email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email đã được sử dụng')
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer cho đăng nhập.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    device = serializers.CharField(max_length=100, required=False, default='Unknown')
    
    def validate(self, data):
        """Validate login credentials"""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Email hoặc mật khẩu không chính xác')
            
            if not user.is_active:
                raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa')
            
            data['user'] = user
        else:
            raise serializers.ValidationError('Email và mật khẩu là bắt buộc')
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer để đổi mật khẩu.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mật khẩu cũ không đúng')
        return value
    
    def validate(self, data):
        """Validate new password confirmation"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Mật khẩu xác nhận không khớp'
            })
        return data
    
    def save(self):
        """Change password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Invalidate all user tokens except current
        current_token = self.context.get('current_token')
        tokens_to_delete = UserToken.objects.filter(user=user)
        if current_token:
            tokens_to_delete = tokens_to_delete.exclude(token=current_token)
        tokens_to_delete.delete()
        
        return user


class UserTokenSerializer(serializers.ModelSerializer):
    """
    Serializer cho UserToken (legacy).
    """
    is_current = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserToken
        fields = [
            'id', 'device_name', 'ip_address', 'user_agent',
            'created_date', 'expired_date', 'is_current', 'is_expired'
        ]
        read_only_fields = [
            'id', 'device_name', 'ip_address', 'user_agent',
            'created_date', 'expired_date'
        ]
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_current(self, obj):
        """Check if this is current token"""
        current_token = self.context.get('current_token')
        return obj.token == current_token if current_token else False
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_expired(self, obj):
        """Check if token is expired"""
        return obj.is_expired()


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer cho UserSession (enhanced).
    """
    is_current = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    session_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'device_name', 'device_type', 'ip_address', 'location',
            'created_at', 'last_activity', 'expires_at', 'is_active',
            'is_current', 'is_expired', 'session_duration'
        ]
        read_only_fields = [
            'id', 'device_name', 'device_type', 'ip_address', 'location',
            'created_at', 'last_activity', 'expires_at', 'is_active'
        ]
    
    def get_is_current(self, obj):
        """Check if this is current session"""
        current_session_key = self.context.get('current_session_key')
        return obj.session_key == current_session_key if current_session_key else False
    
    def get_is_expired(self, obj):
        """Check if session is expired"""
        return obj.is_expired()
    
    def get_session_duration(self, obj):
        """Get session duration in seconds"""
        if obj.logout_at:
            return (obj.logout_at - obj.created_at).total_seconds()
        return (timezone.now() - obj.created_at).total_seconds()


class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer cho LoginHistory.
    """
    session_duration = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'login_method', 'device_name', 'ip_address', 'location',
            'login_date', 'logout_date', 'login_successful', 'failure_reason',
            'session_duration', 'status_display'
        ]
        read_only_fields = [
            'id', 'login_method', 'device_name', 'ip_address', 'location',
            'login_date', 'logout_date', 'login_successful', 'failure_reason',
            'session_duration'
        ]
    
    @extend_schema_field(serializers.CharField)
    def get_status_display(self, obj):
        """Get status display"""
        if obj.login_successful:
            return "✅ Successful"
        return f"❌ Failed: {obj.failure_reason or 'Unknown error'}"


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer để request password reset.
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if email exists"""
        try:
            user = User.objects.get(email=value, is_active=True)
            self.user = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('Email không tồn tại trong hệ thống')
    
    def save(self):
        """Create password reset token"""
        # Deactivate old tokens
        PasswordResetToken.objects.filter(
            user=self.user,
            is_used=False
        ).update(is_used=True)
        
        # Create new token
        reset_token = PasswordResetToken.objects.create(user=self.user)
        return reset_token


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer để confirm password reset.
    """
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_token(self, value):
        """Validate reset token"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid():
                raise serializers.ValidationError('Token đã hết hạn hoặc đã được sử dụng')
            self.reset_token = reset_token
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Token không hợp lệ')
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Mật khẩu xác nhận không khớp'
            })
        return data
    
    def save(self):
        """Reset password"""
        user = self.reset_token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        self.reset_token.mark_as_used()
        
        # Invalidate all tokens
        UserToken.objects.filter(user=user).delete()
        UserSession.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logout_at=timezone.now()
        )
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enhanced JWT token serializer với session tracking.
    """
    device_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate credentials và create session tracking"""
        data = super().validate(attrs)
        
        # Add user info to response (avoid circular import)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.full_name,
            'display_name': self.user.display_name,
            'is_seller': self.user.is_seller,
            'is_customer': self.user.is_customer,
            'is_verified': getattr(self.user, 'is_verified', False),
            'is_active': self.user.is_active,
        }
        
        return data


class LogoutSerializer(serializers.Serializer):
    """
    Serializer cho logout operations.
    """
    refresh = serializers.CharField(required=False, help_text="Refresh token to blacklist")
    reason = serializers.CharField(required=False, help_text="Logout reason (optional)") 