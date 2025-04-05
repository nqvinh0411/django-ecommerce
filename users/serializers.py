from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserToken, LoginHistory

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2',
            'is_seller', 'is_customer', 'is_staff', 'is_superuser'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match.')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_seller', 'phone_number', 'address')


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
