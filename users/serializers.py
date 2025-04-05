from django.contrib.auth import get_user_model
from rest_framework import serializers

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
