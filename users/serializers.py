from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.validators.common import validate_password

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


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc cập nhật thông tin người dùng.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'address')


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


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username_field = 'email'

    """
    Serializer cho việc đăng nhập và lấy JWT token.
    """
    def validate(self, attrs):
        try:
            data = super().validate(attrs)

            access_token = data['access']
            refresh_token = data['refresh']

            user = self.user

            print(f"User authenticated: {user.username} (ID: {user.id})")
            
            # Lấy thông tin request
            request = self.context['request']
            device = request.data.get('device', 'Unknown')
            ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')

            token = RefreshToken.for_user(user)
            access = token.access_token
            expired_date = timezone.now() + access.lifetime

            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            return {
                'access': access_token,
                'refresh': refresh_token,
                'expires_in': int(access.lifetime.total_seconds()),
                'token_type': 'Bearer',
                'user': UserSerializer(user).data
            }
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            print(traceback.format_exc())
            raise
