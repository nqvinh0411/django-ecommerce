"""
Product API Contract Tests.

Module này kiểm tra xem Product API có tuân thủ định dạng chuẩn đã
định nghĩa trong tài liệu API hay không.
"""

from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from products.models import Product, Category
from .base import BaseContractTestCase

User = get_user_model()


class ProductAPIContractTestCase(BaseContractTestCase):
    """
    Test case cho việc kiểm tra contract của Product API.
    
    Đảm bảo rằng tất cả các endpoints liên quan đến Product
    đều tuân thủ định dạng response đã chuẩn hóa.
    """
    
    def setUp(self):
        """Chuẩn bị dữ liệu test."""
        # Tạo user để xác thực
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Tạo category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description'
        )
        
        # Tạo product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price=100.00,
            stock=10,
            category=self.category,
            seller=self.user
        )
        
        # URLs
        self.product_list_url = reverse('products_v1:list')
        self.product_detail_url = reverse('products_v1:detail', args=[self.product.id])
        self.product_create_url = reverse('products_v1:create')
        self.product_update_url = reverse('products_v1:update', args=[self.product.id])
        self.product_delete_url = reverse('products_v1:delete', args=[self.product.id])
        
        # Xác thực
        self.client.force_authenticate(user=self.user)
    
    def test_product_list_format(self):
        """Kiểm tra định dạng response của product list API."""
        response = self.client.get(self.product_list_url)
        self.assert_paginated_response_format(response)
        
        # Kiểm tra cấu trúc dữ liệu product
        data = response.data['data']
        self.assertIsInstance(data, list)
        if data:
            product = data[0]
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('price', product)
            self.assertIn('category', product)
    
    def test_product_detail_format(self):
        """Kiểm tra định dạng response của product detail API."""
        response = self.client.get(self.product_detail_url)
        self.assert_success_response_format(response)
        
        # Kiểm tra cấu trúc dữ liệu product
        product = response.data['data']
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertIn('description', product)
        self.assertIn('price', product)
        self.assertIn('category', product)
        self.assertIn('seller', product)
        self.assertIn('created_at', product)
        self.assertIn('updated_at', product)
    
    def test_product_create_format(self):
        """Kiểm tra định dạng response của product create API."""
        data = {
            'name': 'New Test Product',
            'description': 'New test product description',
            'price': 200.00,
            'stock': 20,
            'category': self.category.id
        }
        response = self.client.post(self.product_create_url, data, format='json')
        self.assert_success_response_format(response, status.HTTP_201_CREATED)
        
        # Kiểm tra cấu trúc dữ liệu product mới
        product = response.data['data']
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertEqual(product['name'], 'New Test Product')
        self.assertIn('price', product)
        self.assertEqual(product['price'], '200.00')
    
    def test_product_update_format(self):
        """Kiểm tra định dạng response của product update API."""
        data = {
            'name': 'Updated Test Product',
            'description': 'Updated test product description'
        }
        response = self.client.patch(self.product_update_url, data, format='json')
        self.assert_success_response_format(response)
        
        # Kiểm tra cấu trúc dữ liệu product cập nhật
        product = response.data['data']
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertEqual(product['name'], 'Updated Test Product')
        self.assertIn('description', product)
        self.assertEqual(product['description'], 'Updated test product description')
    
    def test_product_delete_format(self):
        """Kiểm tra định dạng response của product delete API."""
        response = self.client.delete(self.product_delete_url)
        self.assert_success_response_format(response, status.HTTP_204_NO_CONTENT)
    
    def test_validation_error_format(self):
        """Kiểm tra định dạng response khi có lỗi validation."""
        # Thiếu trường bắt buộc
        data = {
            'description': 'Incomplete product data'
        }
        response = self.client.post(self.product_create_url, data, format='json')
        self.assert_validation_error(response)
        
        # Kiểm tra chi tiết lỗi
        self.assertIn('errors', response.data)
        errors = response.data['errors']
        self.assertIn('name', errors)  # Thiếu trường name
        self.assertIn('price', errors)  # Thiếu trường price
        self.assertIn('category', errors)  # Thiếu trường category
    
    def test_authentication_error_format(self):
        """Kiểm tra định dạng response khi không có xác thực."""
        # Logout
        self.client.force_authenticate(user=None)
        
        # Thử tạo product mới
        data = {
            'name': 'Unauthenticated Product',
            'price': 150.00,
            'category': self.category.id
        }
        response = self.client.post(self.product_create_url, data, format='json')
        self.assert_authentication_error(response)
    
    def test_not_found_error_format(self):
        """Kiểm tra định dạng response khi không tìm thấy resource."""
        # ID không tồn tại
        non_existent_id = 9999
        url = reverse('products_v1:detail', args=[non_existent_id])
        response = self.client.get(url)
        self.assert_not_found_error(response)
