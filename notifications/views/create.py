"""
Notification create view module
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Notification


class NotificationCreateView(APIView):
    """
    API để tạo một thông báo cụ thể.
    POST /notifications/{id}/create
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, pk):
        """
        Tạo mới một thông báo cụ thể.
        Người dùng chỉ có thể xóa thông báo của chính họ.
        """
        pass
