"""
Utilities for testing.

Module này cung cấp các hàm và lớp tiện ích để hỗ trợ việc viết test
trong toàn bộ hệ thống E-commerce.
"""
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class TestDataGenerator:
    """
    Tiện ích để tạo dữ liệu test chuẩn hóa cho các module khác nhau.
    """
    
    @staticmethod
    def create_user(role='regular', custom_data=None):
        """
        Tạo người dùng với vai trò xác định.
        
        Args:
            role (str): Vai trò của người dùng ('admin', 'staff', 'regular')
            custom_data (dict): Dữ liệu tùy chỉnh
            
        Returns:
            User: Đối tượng User đã tạo
        """
        data = {
            'admin': {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'adminpassword123',
                'is_staff': True,
                'is_superuser': True,
            },
            'staff': {
                'username': 'staff',
                'email': 'staff@example.com',
                'password': 'staffpassword123',
                'is_staff': True,
                'is_superuser': False,
            },
            'regular': {
                'username': 'user',
                'email': 'user@example.com',
                'password': 'userpassword123',
                'is_staff': False,
                'is_superuser': False,
            }
        }
        
        user_data = data.get(role, data['regular'])
        
        # Cập nhật với dữ liệu tùy chỉnh nếu có
        if custom_data:
            user_data.update(custom_data)
            
        return User.objects.create_user(**user_data)

    @staticmethod
    def create_date_range(days_before=0, days_after=30):
        """
        Tạo khoảng thời gian từ ngày hiện tại.
        
        Args:
            days_before (int): Số ngày trước ngày hiện tại
            days_after (int): Số ngày sau ngày hiện tại
            
        Returns:
            tuple: (start_date, end_date)
        """
        now = timezone.now()
        start_date = now - timedelta(days=days_before)
        end_date = now + timedelta(days=days_after)
        return start_date, end_date


class BaseAPITestCase:
    """
    Lớp TestCase cơ sở cho API tests với các phương thức hỗ trợ.
    """
    
    def setUp(self):
        """Set up common test data."""
        self.client = APIClient()
        self.users = {}
        
        # Tạo người dùng với các vai trò khác nhau
        self.users['admin'] = TestDataGenerator.create_user('admin')
        self.users['staff'] = TestDataGenerator.create_user('staff')
        self.users['regular'] = TestDataGenerator.create_user('regular')
    
    def authenticate(self, role='admin'):
        """
        Xác thực client với người dùng có vai trò cụ thể.
        
        Args:
            role (str): Vai trò của người dùng ('admin', 'staff', 'regular')
        """
        self.client.force_authenticate(user=self.users.get(role))
    
    def logout(self):
        """Đăng xuất client."""
        self.client.force_authenticate(user=None)
    
    def assert_status(self, response, expected_status):
        """
        Kiểm tra mã trạng thái của response.
        
        Args:
            response: Response từ API client
            expected_status (int): Mã trạng thái mong đợi
        """
        self.assertEqual(response.status_code, expected_status)
        
    def assert_response_format(self, response):
        """
        Kiểm tra format chuẩn của response API.
        
        Args:
            response: Response từ API client
            
        Returns:
            bool: True nếu response có format chuẩn
        """
        self.assertIn('status', response.data)
        self.assertIn('status_code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        return True
    
    def assert_forbidden_for_role(self, url, method='get', role='regular', data=None):
        """
        Kiểm tra xem một vai trò có bị từ chối truy cập hay không.
        
        Args:
            url (str): URL để kiểm tra
            method (str): HTTP method ('get', 'post', 'put', 'patch', 'delete')
            role (str): Vai trò để kiểm tra ('admin', 'staff', 'regular')
            data (dict): Dữ liệu để gửi trong request
            
        Returns:
            bool: True nếu truy cập bị từ chối (403)
        """
        self.authenticate(role)
        
        method_func = getattr(self.client, method.lower())
        if data and method.lower() != 'get':
            response = method_func(url, data=data, format='json')
        else:
            response = method_func(url)
            
        self.assertEqual(response.status_code, 403)
        return True
