from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")

    def test_register(self):
        """Test đăng ký người dùng mới"""
        data = {"username": "newuser", "email": "new@example.com", "password": "testpass", "password2": "testpass"}
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_existing_username(self):
        """Test đăng ký với username đã tồn tại"""
        data = {"username": "testuser", "email": "new@example.com", "password": "testpass", "password2": "testpass"}
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_mismatched_passwords(self):
        """Test đăng ký với mật khẩu không khớp"""
        data = {"username": "newuser", "email": "new@example.com", "password": "testpass", "password2": "wrongpass"}
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        """Test đăng nhập thành công"""
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post("/api/auth/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_with_wrong_password(self):
        """Test đăng nhập với sai mật khẩu"""
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post("/api/auth/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_info(self):
        """Test lấy thông tin user khi đã đăng nhập"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/user/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_info_without_authentication(self):
        """Test lấy thông tin user khi chưa đăng nhập"""
        response = self.client.get("/api/auth/user/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
