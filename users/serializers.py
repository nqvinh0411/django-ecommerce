from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

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


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer cho user profile information.
    """
    full_name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'display_name', 'role_display',
            'phone_number', 'address', 'date_of_birth', 'avatar',
            'is_seller', 'is_customer', 'is_verified', 'is_active',
            'last_login', 'last_login_ip', 'created_at'
        ]
        read_only_fields = [
            'id', 'email', 'full_name', 'display_name', 'role_display',
            'is_verified', 'last_login', 'last_login_ip', 'created_at'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer để update user profile chi tiết.
    """
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role_display', 'phone_number', 'address',
            'date_of_birth', 'avatar', 'is_seller', 'is_customer',
            'is_verified', 'is_active', 'last_login', 'created_at'
        ]
        read_only_fields = [
            'id', 'email', 'username', 'full_name', 'role_display',
            'is_verified', 'last_login', 'created_at'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError('Số điện thoại không hợp lệ')
        return value


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer để admin update user roles.
    """
    class Meta:
        model = User
        fields = ['is_seller', 'is_customer', 'is_staff', 'is_active']
    
    def validate(self, data):
        """Ensure user has at least one role"""
        if not data.get('is_seller', False) and not data.get('is_customer', False) and not data.get('is_staff', False):
            raise serializers.ValidationError('User phải có ít nhất một role')
        return data


class UserAnalyticsSerializer(serializers.Serializer):
    """
    Serializer cho user analytics data.
    """
    total_users = serializers.IntegerField(read_only=True)
    active_users = serializers.IntegerField(read_only=True)
    verified_users = serializers.IntegerField(read_only=True)
    seller_users = serializers.IntegerField(read_only=True)
    customer_users = serializers.IntegerField(read_only=True)
    recent_registrations = serializers.IntegerField(read_only=True)
    recently_active = serializers.IntegerField(read_only=True)
    verification_rate = serializers.FloatField(read_only=True)
    activity_rate = serializers.FloatField(read_only=True)
    registration_trend = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
