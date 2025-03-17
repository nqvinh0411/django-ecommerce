from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from notifications.models import Notification

User = get_user_model()

class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.notification = Notification.objects.create(user=self.user, message="Đơn hàng của bạn đã được xác nhận!")
        self.client.force_authenticate(user=self.user)

    def test_get_notifications(self):
        """Test lấy danh sách thông báo"""
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_notification(self):
        """Test xóa thông báo"""
        response = self.client.delete(f"/api/notifications/{self.notification.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
