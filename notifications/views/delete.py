"""
Notification delete view module
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Notification


class NotificationDeleteView(APIView):
    """
    API để xóa một thông báo cụ thể.
    DELETE /notifications/{id}/delete
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        """
        Xóa một thông báo cụ thể. 
        Người dùng chỉ có thể xóa thông báo của chính họ.
        """
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.delete()
            return Response(
                {"message": "Notification deleted successfully"}, 
                status=status.HTTP_200_OK
            )
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
