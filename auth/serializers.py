from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserToken, LoginHistory

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields  = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_customer = True
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    device_name = serializers.CharField(required=False, default='Unknown')
    

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"Mật khẩu mới không khớp"})
        return attrs
    
class UserTokenSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = UserToken
        fields = ('id', 'device_name', 'ip_address', 'created_date', 'is_current')
        
    def get_is_current(self, obj):
        request = self.context.get('request')
        if request:
            current_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
            return obj.token == current_token
        return False
    
class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ('id', 'device_name', 'ip_address', 'login_date', 'logout_date')