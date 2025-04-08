"""
Notification update view module
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Notification


class NotificationUpdateView(APIView):
    """
    API để cập nhật một thông báo cụ thể.
    PUT /notifications/{id}/update
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        """
        Xóa một thông báo cụ thể.
        Người dùng chỉ có thể xóa thông báo của chính họ.
        """
        pass
