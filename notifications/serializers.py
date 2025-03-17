from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at']
