"""
Unit tests for Inventory ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Inventory,
bao gồm WarehouseViewSet, StockItemViewSet và StockMovementViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, ProductVariant
from ..models import Warehouse, StockItem, StockMovement
from ..serializers import WarehouseSerializer, StockItemSerializer, StockMovementSerializer

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class WarehouseViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for WarehouseViewSet.
    """
    
    model_class = Warehouse
    serializer_class = WarehouseSerializer
    base_url_name = 'warehouses'
    
    valid_create_data = {
        'name': 'Test Warehouse',
        'code': 'TST001',
        'address': '123 Test Street',
        'city': 'Test City',
        'state': 'Test State',
        'country': 'Test Country',
        'postal_code': '12345',
        'is_active': True
    }
    
    valid_update_data = {
        'name': 'Updated Warehouse',
        'address': '456 Updated Street',
        'is_active': False
    }
    
    def setUp(self):
        """Set up specific test data for Warehouse."""
        super().setUp()
        
        # Tạo dữ liệu test cho Warehouse
        self.warehouse1 = Warehouse.objects.create(
            name='Warehouse 1',
            code='WH001',
            address='123 Main Street',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            is_active=True
        )
        
        self.warehouse2 = Warehouse.objects.create(
            name='Warehouse 2',
            code='WH002',
            address='456 Second Street',
            city='Los Angeles',
            state='CA',
            country='USA',
            postal_code='90001',
            is_active=True
        )
    
    def test_filter_by_active_status(self):
        """Test filtering warehouses by active status."""
        # Đặt warehouse2 thành không hoạt động
        self.warehouse2.is_active = False
        self.warehouse2.save()
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về kho hoạt động
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Warehouse 1')
    
    def test_search_by_name(self):
        """Test tìm kiếm kho theo tên."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=Warehouse 1")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về kho có tên phù hợp
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Warehouse 1')


class StockItemViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for StockItemViewSet.
    """
    
    model_class = StockItem
    serializer_class = StockItemSerializer
    base_url_name = 'stock-items'
    
    def setUp(self):
        """Set up specific test data for StockItem."""
        super().setUp()
        
        # Tạo dữ liệu test cho Warehouse
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            code='TEST',
            address='123 Test Street',
            city='Test City',
            state='Test State',
            country='Test Country',
            postal_code='12345',
            is_active=True
        )
        
        # Tạo dữ liệu test cho Product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price=100.0,
            is_active=True
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'product_id': self.product.id,
            'warehouse_id': self.warehouse.id,
            'quantity': 10,
            'min_stock_level': 5,
            'max_stock_level': 20
        }
        
        self.valid_update_data = {
            'quantity': 15,
            'min_stock_level': 3,
            'max_stock_level': 25
        }
        
        # Tạo một số StockItem cho test
        self.stock_item = StockItem.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantity=10,
            min_stock_level=5,
            max_stock_level=20
        )
    
    def test_filter_by_warehouse(self):
        """Test lọc các mục kho theo kho."""
        # Tạo kho thứ hai
        warehouse2 = Warehouse.objects.create(
            name='Second Warehouse',
            code='SEC',
            address='456 Second Street',
            city='Second City',
            state='SS',
            country='Second Country',
            postal_code='67890',
            is_active=True
        )
        
        # Tạo StockItem trong kho thứ hai
        StockItem.objects.create(
            product=self.product,
            warehouse=warehouse2,
            quantity=5,
            min_stock_level=2,
            max_stock_level=10
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?warehouse_id={self.warehouse.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về StockItem trong kho đầu tiên
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['warehouse']['id'], self.warehouse.id)
    
    def test_filter_by_low_stock(self):
        """Test lọc các mục kho có lượng tồn thấp."""
        # Cập nhật StockItem để có lượng tồn thấp
        self.stock_item.quantity = 3  # Dưới min_stock_level
        self.stock_item.save()
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?low_stock=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về StockItem có lượng tồn thấp
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['id'], self.stock_item.id)
    
    def test_adjust_stock_endpoint(self):
        """Test endpoint điều chỉnh kho."""
        # Chuẩn bị dữ liệu
        adjust_data = {
            'quantity': 5,
            'reason': 'Manual adjustment',
            'adjustment_type': 'increase'
        }
        
        # Gọi API
        url = reverse(f'api:{self.base_url_name}-adjust-stock', args=[self.stock_item.id])
        response = self.client.post(url, adjust_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng đã được cập nhật
        self.stock_item.refresh_from_db()
        self.assertEqual(self.stock_item.quantity, 15)  # 10 + 5
        
        # Kiểm tra đã tạo StockMovement
        self.assertEqual(StockMovement.objects.count(), 1)
        movement = StockMovement.objects.first()
        self.assertEqual(movement.stock_item, self.stock_item)
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.reason, 'Manual adjustment')


class StockMovementViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for StockMovementViewSet.
    """
    
    model_class = StockMovement
    serializer_class = StockMovementSerializer
    base_url_name = 'stock-movements'
    
    def setUp(self):
        """Set up specific test data for StockMovement."""
        super().setUp()
        
        # Tạo dữ liệu test cho Warehouse
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            code='TEST',
            address='123 Test Street',
            city='Test City',
            state='Test State',
            country='Test Country',
            postal_code='12345',
            is_active=True
        )
        
        # Tạo dữ liệu test cho Product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price=100.0,
            is_active=True
        )
        
        # Tạo StockItem
        self.stock_item = StockItem.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantity=10,
            min_stock_level=5,
            max_stock_level=20
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'stock_item_id': self.stock_item.id,
            'quantity': 5,
            'movement_type': 'incoming',
            'reason': 'Test movement',
            'reference_number': 'REF001'
        }
        
        self.valid_update_data = {
            'reason': 'Updated test movement',
            'reference_number': 'REF002'
        }
        
        # Tạo một số StockMovement cho test
        self.stock_movement = StockMovement.objects.create(
            stock_item=self.stock_item,
            quantity=5,
            movement_type='incoming',
            reason='Initial movement',
            reference_number='INIT001'
        )
    
    def test_filter_by_movement_type(self):
        """Test lọc chuyển động kho theo loại."""
        # Tạo chuyển động kho thứ hai
        StockMovement.objects.create(
            stock_item=self.stock_item,
            quantity=3,
            movement_type='outgoing',
            reason='Outgoing movement',
            reference_number='OUT001'
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?movement_type=incoming")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về chuyển động kho nhập
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['movement_type'], 'incoming')
    
    def test_filter_by_date_range(self):
        """Test lọc chuyển động kho theo khoảng thời gian."""
        # Tạo chuyển động kho với thời gian cụ thể
        yesterday = timezone.now() - timezone.timedelta(days=1)
        yesterday_movement = StockMovement.objects.create(
            stock_item=self.stock_item,
            quantity=2,
            movement_type='incoming',
            reason='Yesterday movement',
            reference_number='YES001',
            created_at=yesterday
        )
        
        # Gọi API với filter
        today = timezone.now().date().isoformat()
        response = self.client.get(f"{self.list_url}?start_date={today}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về chuyển động kho của hôm nay
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['id'], self.stock_movement.id)
    
    def test_report_endpoint(self):
        """Test endpoint báo cáo chuyển động kho."""
        # Tạo thêm một số chuyển động kho
        StockMovement.objects.create(
            stock_item=self.stock_item,
            quantity=3,
            movement_type='outgoing',
            reason='Outgoing movement 1',
            reference_number='OUT001'
        )
        
        StockMovement.objects.create(
            stock_item=self.stock_item,
            quantity=2,
            movement_type='outgoing',
            reason='Outgoing movement 2',
            reference_number='OUT002'
        )
        
        # Gọi API
        url = reverse('api:stock-movement-report')
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra báo cáo
        self.assertIn('total_movements', response.data['data'])
        self.assertIn('incoming_total', response.data['data'])
        self.assertIn('outgoing_total', response.data['data'])
        
        # Kiểm tra tổng số
        self.assertEqual(response.data['data']['total_movements'], 3)
        self.assertEqual(response.data['data']['incoming_total'], 5)  # Tổng số nhập
        self.assertEqual(response.data['data']['outgoing_total'], 5)  # Tổng số xuất (3+2)
