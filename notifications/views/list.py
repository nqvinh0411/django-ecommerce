"""
Notification list view module
"""
from rest_framework import permissions

from core.views.base import BaseListView
from ..models import Notification
from ..serializers import NotificationSerializer


class NotificationListView(BaseListView):
    """
    API để liệt kê tất cả các thông báo của người dùng đã đăng nhập.
    GET /notifications/
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Trả về tất cả thông báo của người dùng hiện tại.
        """
        return Notification.objects.filter(user=self.request.user)
