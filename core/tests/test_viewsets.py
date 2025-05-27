"""
Tests for StandardizedModelViewSet.

Module này cung cấp các test case cơ sở cho các ViewSet chuẩn hóa,
có thể được kế thừa bởi các test trong từng module cụ thể.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .test_utils import BaseAPITestCase, TestDataGenerator


class StandardizedViewSetTestCase(BaseAPITestCase):
    """
    Test case cơ sở cho các StandardizedModelViewSet.
    
    Cung cấp các phương thức test chuẩn cho CRUD operations.
    Các lớp con cần ghi đè các thuộc tính sau:
    - model_class: Lớp model
    - serializer_class: Lớp serializer
    - base_url_name: Tên URL cơ sở
    - valid_create_data: Dữ liệu hợp lệ để tạo đối tượng mới
    - valid_update_data: Dữ liệu hợp lệ để cập nhật đối tượng
    - required_permissions: Quyền cần thiết để truy cập ViewSet
    """
    
    model_class = None
    serializer_class = None
    base_url_name = None
    valid_create_data = {}
    valid_update_data = {}
    required_permissions = []
    
    def setUp(self):
        """Set up base test data."""
        super().setUp()
        
        # Tạo các đường dẫn URL
        self.list_url = reverse(f'api:{self.base_url_name}-list')
        
        # Đăng nhập với vai trò admin
        self.authenticate('admin')
    
    def get_detail_url(self, pk):
        """Lấy URL chi tiết cho một đối tượng."""
        return reverse(f'api:{self.base_url_name}-detail', args=[pk])
    
    def create_instance(self, **kwargs):
        """
        Tạo một instance của model.
        
        Args:
            **kwargs: Các tham số để tạo instance
            
        Returns:
            model_instance: Instance của model
        """
        return self.model_class.objects.create(**kwargs)
    
    def test_list_endpoint(self):
        """Test endpoint danh sách."""
        # Tạo một số instance
        for i in range(3):
            self.create_instance(**self.valid_create_data)
        
        # Gọi API
        response = self.client.get(self.list_url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        self.assert_response_format(response)
        
        # Kiểm tra số lượng items
        self.assertEqual(len(response.data['data']), 3)
    
    def test_retrieve_endpoint(self):
        """Test endpoint xem chi tiết."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Gọi API
        url = self.get_detail_url(instance.id)
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        self.assert_response_format(response)
        
        # Kiểm tra dữ liệu
        self.assertEqual(response.data['data']['id'], instance.id)
    
    def test_create_endpoint(self):
        """Test endpoint tạo mới."""
        # Số lượng ban đầu
        initial_count = self.model_class.objects.count()
        
        # Gọi API
        response = self.client.post(
            self.list_url,
            self.valid_create_data,
            format='json'
        )
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        self.assert_response_format(response)
        
        # Kiểm tra số lượng sau khi tạo
        self.assertEqual(self.model_class.objects.count(), initial_count + 1)
    
    def test_update_endpoint(self):
        """Test endpoint cập nhật."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Gọi API
        url = self.get_detail_url(instance.id)
        response = self.client.put(
            url,
            self.valid_update_data,
            format='json'
        )
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        self.assert_response_format(response)
        
        # Kiểm tra dữ liệu đã được cập nhật
        instance.refresh_from_db()
        for key, value in self.valid_update_data.items():
            self.assertEqual(getattr(instance, key), value)
    
    def test_partial_update_endpoint(self):
        """Test endpoint cập nhật một phần."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Chỉ lấy một phần của dữ liệu cập nhật
        partial_data = {k: v for k, v in list(self.valid_update_data.items())[:1]}
        
        # Gọi API
        url = self.get_detail_url(instance.id)
        response = self.client.patch(
            url,
            partial_data,
            format='json'
        )
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        self.assert_response_format(response)
        
        # Kiểm tra dữ liệu đã được cập nhật
        instance.refresh_from_db()
        for key, value in partial_data.items():
            self.assertEqual(getattr(instance, key), value)
    
    def test_delete_endpoint(self):
        """Test endpoint xóa."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Gọi API
        url = self.get_detail_url(instance.id)
        response = self.client.delete(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra instance đã bị xóa
        self.assertEqual(self.model_class.objects.filter(id=instance.id).count(), 0)
    
    def test_permissions_for_list(self):
        """Test quyền truy cập cho endpoint danh sách."""
        # Kiểm tra với vai trò regular
        self.assert_forbidden_for_role(self.list_url, role='regular')
    
    def test_permissions_for_detail(self):
        """Test quyền truy cập cho endpoint chi tiết."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Kiểm tra với vai trò regular
        url = self.get_detail_url(instance.id)
        self.assert_forbidden_for_role(url, role='regular')
    
    def test_permissions_for_create(self):
        """Test quyền truy cập cho endpoint tạo mới."""
        # Kiểm tra với vai trò regular
        self.assert_forbidden_for_role(
            self.list_url,
            method='post',
            role='regular',
            data=self.valid_create_data
        )
    
    def test_permissions_for_update(self):
        """Test quyền truy cập cho endpoint cập nhật."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Kiểm tra với vai trò regular
        url = self.get_detail_url(instance.id)
        self.assert_forbidden_for_role(
            url,
            method='put',
            role='regular',
            data=self.valid_update_data
        )
    
    def test_permissions_for_delete(self):
        """Test quyền truy cập cho endpoint xóa."""
        # Tạo instance
        instance = self.create_instance(**self.valid_create_data)
        
        # Kiểm tra với vai trò regular
        url = self.get_detail_url(instance.id)
        self.assert_forbidden_for_role(
            url,
            method='delete',
            role='regular'
        )
