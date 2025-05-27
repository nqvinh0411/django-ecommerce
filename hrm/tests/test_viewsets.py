"""
Unit tests for HRM ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module HRM,
bao gồm DepartmentViewSet, EmployeeViewSet, và PositionViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Department, Employee, Position
from ..serializers import DepartmentSerializer, EmployeeSerializer, PositionSerializer

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class DepartmentViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for DepartmentViewSet.
    """
    
    model_class = Department
    serializer_class = DepartmentSerializer
    base_url_name = 'departments'
    
    valid_create_data = {
        'name': 'Test Department',
        'code': 'TEST',
        'description': 'This is a test department',
        'is_active': True
    }
    
    valid_update_data = {
        'name': 'Updated Department',
        'description': 'This is an updated department description'
    }
    
    def setUp(self):
        """Set up specific test data for Department."""
        super().setUp()
        
        # Tạo department
        self.sales_dept = Department.objects.create(
            name='Sales',
            code='SALES',
            description='Sales department',
            is_active=True
        )
        
        self.marketing_dept = Department.objects.create(
            name='Marketing',
            code='MKT',
            description='Marketing department',
            is_active=True
        )
        
        self.inactive_dept = Department.objects.create(
            name='Inactive Department',
            code='INACT',
            description='This department is inactive',
            is_active=False
        )
    
    def test_filter_by_is_active(self):
        """Test lọc phòng ban theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về phòng ban đang hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra phòng ban không hoạt động không được trả về
        department_names = [dept['name'] for dept in response.data['data']]
        self.assertNotIn('Inactive Department', department_names)
    
    def test_search_by_name_or_code(self):
        """Test tìm kiếm phòng ban theo tên hoặc mã."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=sal")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về phòng ban có 'sal' trong tên hoặc mã
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Sales')
    
    def test_get_department_employees(self):
        """Test lấy danh sách nhân viên trong phòng ban."""
        # Tạo position
        position = Position.objects.create(
            name='Sales Representative',
            department=self.sales_dept,
            is_active=True
        )
        
        # Tạo nhân viên
        employee = Employee.objects.create(
            user=self.users['regular'],
            first_name='John',
            last_name='Doe',
            department=self.sales_dept,
            position=position,
            email='john.doe@example.com',
            phone='1234567890',
            hire_date=timezone.now().date()
        )
        
        # Gọi API
        url = reverse('api:departments-employees', args=[self.sales_dept.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách nhân viên
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['first_name'], 'John')
        self.assertEqual(response.data['data'][0]['last_name'], 'Doe')


class EmployeeViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for EmployeeViewSet.
    """
    
    model_class = Employee
    serializer_class = EmployeeSerializer
    base_url_name = 'employees'
    
    def setUp(self):
        """Set up specific test data for Employee."""
        super().setUp()
        
        # Tạo department
        self.department = Department.objects.create(
            name='IT',
            code='IT',
            description='IT department',
            is_active=True
        )
        
        # Tạo position
        self.position = Position.objects.create(
            name='Developer',
            department=self.department,
            is_active=True
        )
        
        # Tạo user cho nhân viên
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='employee123'
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'user_id': self.employee_user.id,
            'first_name': 'Test',
            'last_name': 'Employee',
            'department_id': self.department.id,
            'position_id': self.position.id,
            'email': 'test.employee@example.com',
            'phone': '0987654321',
            'hire_date': timezone.now().date().isoformat(),
            'is_active': True
        }
        
        self.valid_update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '1122334455'
        }
        
        # Tạo nhân viên
        self.employee = Employee.objects.create(
            user=self.users['regular'],
            first_name='John',
            last_name='Doe',
            department=self.department,
            position=self.position,
            email='john.doe@example.com',
            phone='1234567890',
            hire_date=timezone.now().date()
        )
    
    def test_filter_by_department(self):
        """Test lọc nhân viên theo phòng ban."""
        # Tạo phòng ban thứ hai
        dept2 = Department.objects.create(
            name='HR',
            code='HR',
            description='Human Resources',
            is_active=True
        )
        
        # Tạo vị trí trong phòng ban thứ hai
        pos2 = Position.objects.create(
            name='HR Manager',
            department=dept2,
            is_active=True
        )
        
        # Tạo nhân viên trong phòng ban thứ hai
        user2 = User.objects.create_user(
            username='hr_employee',
            email='hr@example.com',
            password='hr123'
        )
        
        emp2 = Employee.objects.create(
            user=user2,
            first_name='Jane',
            last_name='Smith',
            department=dept2,
            position=pos2,
            email='jane.smith@example.com',
            phone='0987654321',
            hire_date=timezone.now().date()
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?department_id={self.department.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về nhân viên trong phòng ban IT
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['first_name'], 'John')
    
    def test_search_by_name(self):
        """Test tìm kiếm nhân viên theo tên."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=John")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về nhân viên có tên 'John'
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['first_name'], 'John')
    
    def test_employee_performance_endpoint(self):
        """Test endpoint employee-performance."""
        # Chuẩn bị dữ liệu
        performance_data = {
            'rating': 4.5,
            'review_period': 'Q2 2025',
            'comments': 'Excellent performance in this quarter'
        }
        
        # Gọi API
        url = reverse('api:employees-performance', args=[self.employee.id])
        response = self.client.post(url, performance_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra dữ liệu hiệu suất đã được lưu
        self.assertIn('performance', response.data['data'])
        self.assertEqual(response.data['data']['performance']['rating'], 4.5)
        self.assertEqual(response.data['data']['performance']['review_period'], 'Q2 2025')


class PositionViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for PositionViewSet.
    """
    
    model_class = Position
    serializer_class = PositionSerializer
    base_url_name = 'positions'
    
    def setUp(self):
        """Set up specific test data for Position."""
        super().setUp()
        
        # Tạo department
        self.department = Department.objects.create(
            name='IT',
            code='IT',
            description='IT department',
            is_active=True
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'name': 'Test Position',
            'department_id': self.department.id,
            'is_active': True
        }
        
        self.valid_update_data = {
            'name': 'Updated Position',
            'is_active': False
        }
        
        # Tạo vị trí
        self.position1 = Position.objects.create(
            name='Developer',
            department=self.department,
            is_active=True
        )
        
        self.position2 = Position.objects.create(
            name='System Admin',
            department=self.department,
            is_active=True
        )
        
        self.inactive_position = Position.objects.create(
            name='Inactive Position',
            department=self.department,
            is_active=False
        )
    
    def test_filter_by_department(self):
        """Test lọc vị trí theo phòng ban."""
        # Tạo phòng ban thứ hai
        dept2 = Department.objects.create(
            name='Sales',
            code='SALES',
            description='Sales department',
            is_active=True
        )
        
        # Tạo vị trí trong phòng ban thứ hai
        Position.objects.create(
            name='Sales Representative',
            department=dept2,
            is_active=True
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?department_id={self.department.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về vị trí trong phòng ban IT
        self.assertEqual(len(response.data['data']), 3)  # 2 active + 1 inactive
        
        # Kiểm tra tên vị trí
        position_names = [pos['name'] for pos in response.data['data']]
        self.assertIn('Developer', position_names)
        self.assertIn('System Admin', position_names)
        self.assertNotIn('Sales Representative', position_names)
    
    def test_filter_by_is_active(self):
        """Test lọc vị trí theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về vị trí đang hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra vị trí không hoạt động không được trả về
        position_names = [pos['name'] for pos in response.data['data']]
        self.assertNotIn('Inactive Position', position_names)
    
    def test_get_positions_with_employee_count(self):
        """Test lấy vị trí kèm theo số lượng nhân viên."""
        # Tạo nhân viên cho vị trí Developer
        user1 = User.objects.create_user(
            username='dev1',
            email='dev1@example.com',
            password='dev123'
        )
        
        Employee.objects.create(
            user=user1,
            first_name='Dev',
            last_name='One',
            department=self.department,
            position=self.position1,
            email='dev.one@example.com',
            phone='1111111111',
            hire_date=timezone.now().date()
        )
        
        # Gọi API với parameter include_employee_count
        response = self.client.get(f"{self.list_url}?include_employee_count=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra employee_count được bao gồm trong response
        dev_position = next(pos for pos in response.data['data'] if pos['name'] == 'Developer')
        admin_position = next(pos for pos in response.data['data'] if pos['name'] == 'System Admin')
        
        self.assertIn('employee_count', dev_position)
        self.assertEqual(dev_position['employee_count'], 1)
        
        self.assertIn('employee_count', admin_position)
        self.assertEqual(admin_position['employee_count'], 0)
