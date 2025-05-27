"""
Unit tests for Orders ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Orders,
bao gồm OrderViewSet, OrderItemViewSet, và OrderStatusViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from ..models import Order, OrderItem, OrderStatus, ShippingAddress, PaymentMethod
from ..serializers import OrderSerializer, OrderItemSerializer, OrderStatusSerializer

# Import CartItem model để kiểm thử tính năng create order from cart
try:
    from cart.models import Cart, CartItem
except ImportError:
    # Mock cho mục đích kiểm thử
    Cart = type('Cart', (), {})
    CartItem = type('CartItem', (), {})

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class OrderStatusViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for OrderStatusViewSet.
    """
    
    model_class = OrderStatus
    serializer_class = OrderStatusSerializer
    base_url_name = 'order-statuses'
    
    valid_create_data = {
        'name': 'Test Status',
        'description': 'This is a test status',
        'color': '#FF5733',
        'is_active': True,
        'sort_order': 5
    }
    
    valid_update_data = {
        'name': 'Updated Status',
        'description': 'This is an updated status description',
        'color': '#33FF57'
    }
    
    def setUp(self):
        """Set up specific test data for OrderStatus."""
        super().setUp()
        
        # Tạo trạng thái đơn hàng
        self.status_pending = OrderStatus.objects.create(
            name='Pending',
            description='Order has been placed but not yet processed',
            color='#FFC107',
            is_active=True,
            sort_order=1
        )
        
        self.status_processing = OrderStatus.objects.create(
            name='Processing',
            description='Order is being processed',
            color='#2196F3',
            is_active=True,
            sort_order=2
        )
        
        self.status_shipped = OrderStatus.objects.create(
            name='Shipped',
            description='Order has been shipped',
            color='#4CAF50',
            is_active=True,
            sort_order=3
        )
        
        self.status_delivered = OrderStatus.objects.create(
            name='Delivered',
            description='Order has been delivered',
            color='#8BC34A',
            is_active=True,
            sort_order=4
        )
        
        self.status_cancelled = OrderStatus.objects.create(
            name='Cancelled',
            description='Order has been cancelled',
            color='#F44336',
            is_active=True,
            sort_order=5
        )
        
        self.status_inactive = OrderStatus.objects.create(
            name='Inactive Status',
            description='This status is inactive',
            color='#9E9E9E',
            is_active=False,
            sort_order=6
        )
    
    def test_filter_by_is_active(self):
        """Test lọc trạng thái theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về trạng thái đang hoạt động
        self.assertEqual(len(response.data['data']), 5)
        
        # Kiểm tra trạng thái không hoạt động không được trả về
        status_names = [stat['name'] for stat in response.data['data']]
        self.assertNotIn('Inactive Status', status_names)
    
    def test_ordering_by_sort_order(self):
        """Test sắp xếp trạng thái theo sort_order."""
        # Gọi API với ordering
        response = self.client.get(f"{self.list_url}?ordering=sort_order")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra thứ tự trạng thái
        status_names = [stat['name'] for stat in response.data['data']]
        expected_order = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Inactive Status']
        
        # Kiểm tra 5 trạng thái đầu tiên
        for i in range(5):
            self.assertEqual(status_names[i], expected_order[i])


class OrderViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for OrderViewSet.
    """
    
    model_class = Order
    serializer_class = OrderSerializer
    base_url_name = 'orders'
    
    def setUp(self):
        """Set up specific test data for Order."""
        super().setUp()
        
        # Tạo trạng thái đơn hàng
        self.status_pending = OrderStatus.objects.create(
            name='Pending',
            description='Order has been placed but not yet processed',
            color='#FFC107',
            is_active=True,
            sort_order=1
        )
        
        self.status_processing = OrderStatus.objects.create(
            name='Processing',
            description='Order is being processed',
            color='#2196F3',
            is_active=True,
            sort_order=2
        )
        
        self.status_delivered = OrderStatus.objects.create(
            name='Delivered',
            description='Order has been delivered',
            color='#8BC34A',
            is_active=True,
            sort_order=4
        )
        
        # Tạo địa chỉ giao hàng
        self.shipping_address = ShippingAddress.objects.create(
            user=self.users['regular'],
            recipient_name='John Doe',
            address_line1='123 Main St',
            address_line2='Apt 4B',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            phone='1234567890',
            is_default=True
        )
        
        # Tạo phương thức thanh toán
        self.payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            code='credit_card',
            description='Pay with credit card',
            is_active=True
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'user_id': self.users['regular'].id,
            'order_number': 'ORD-TEST-001',
            'order_status_id': self.status_pending.id,
            'shipping_address_id': self.shipping_address.id,
            'payment_method_id': self.payment_method.id,
            'shipping_cost': '10.00',
            'tax_amount': '20.00',
            'discount_amount': '5.00',
            'subtotal': '100.00',
            'total': '125.00',
            'notes': 'Test order'
        }
        
        self.valid_update_data = {
            'order_status_id': self.status_processing.id,
            'notes': 'Updated order notes'
        }
        
        # Tạo đơn hàng
        self.order1 = Order.objects.create(
            user=self.users['regular'],
            order_number='ORD-001',
            order_status=self.status_pending,
            shipping_address=self.shipping_address,
            payment_method=self.payment_method,
            order_date=timezone.now(),
            shipping_cost=Decimal('10.00'),
            tax_amount=Decimal('20.00'),
            discount_amount=Decimal('5.00'),
            subtotal=Decimal('100.00'),
            total=Decimal('125.00')
        )
        
        self.order2 = Order.objects.create(
            user=self.users['regular'],
            order_number='ORD-002',
            order_status=self.status_processing,
            shipping_address=self.shipping_address,
            payment_method=self.payment_method,
            order_date=timezone.now() - timedelta(days=1),
            shipping_cost=Decimal('10.00'),
            tax_amount=Decimal('15.00'),
            discount_amount=Decimal('0.00'),
            subtotal=Decimal('75.00'),
            total=Decimal('100.00')
        )
        
        self.order3 = Order.objects.create(
            user=self.users['regular'],
            order_number='ORD-003',
            order_status=self.status_delivered,
            shipping_address=self.shipping_address,
            payment_method=self.payment_method,
            order_date=timezone.now() - timedelta(days=7),
            shipping_cost=Decimal('10.00'),
            tax_amount=Decimal('30.00'),
            discount_amount=Decimal('10.00'),
            subtotal=Decimal('150.00'),
            total=Decimal('180.00')
        )
        
        # Tạo order item
        self.order_item1 = OrderItem.objects.create(
            order=self.order1,
            product_name='Product 1',
            sku='SKU-001',
            quantity=2,
            unit_price=Decimal('50.00'),
            subtotal=Decimal('100.00')
        )
    
    def test_filter_by_order_status(self):
        """Test lọc đơn hàng theo trạng thái."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?order_status_id={self.status_pending.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về đơn hàng có trạng thái Pending
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['order_number'], 'ORD-001')
    
    def test_filter_by_date_range(self):
        """Test lọc đơn hàng theo khoảng thời gian."""
        # Gọi API với filter
        yesterday = (timezone.now() - timedelta(days=1)).date().isoformat()
        today = timezone.now().date().isoformat()
        
        response = self.client.get(f"{self.list_url}?start_date={yesterday}&end_date={today}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về đơn hàng trong khoảng thời gian
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra đơn hàng cũ hơn không được trả về
        order_numbers = [order['order_number'] for order in response.data['data']]
        self.assertIn('ORD-001', order_numbers)
        self.assertIn('ORD-002', order_numbers)
        self.assertNotIn('ORD-003', order_numbers)
    
    def test_search_by_order_number(self):
        """Test tìm kiếm đơn hàng theo số đơn hàng."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=ORD-001")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về đơn hàng có số ORD-001
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['order_number'], 'ORD-001')
    
    def test_order_items_endpoint(self):
        """Test endpoint lấy các mục đơn hàng."""
        # Gọi API
        url = reverse('api:orders-items', args=[self.order1.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách mục đơn hàng
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['product_name'], 'Product 1')
        self.assertEqual(response.data['data'][0]['quantity'], 2)
    
    def test_update_order_status_endpoint(self):
        """Test endpoint cập nhật trạng thái đơn hàng."""
        # Chuẩn bị dữ liệu
        status_data = {
            'order_status_id': self.status_delivered.id,
            'notes': 'Order has been delivered'
        }
        
        # Gọi API
        url = reverse('api:orders-update-status', args=[self.order1.id])
        response = self.client.post(url, status_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra trạng thái đơn hàng đã được cập nhật
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.order_status.id, self.status_delivered.id)
        self.assertEqual(self.order1.notes, 'Order has been delivered')
    
    def test_order_summary_endpoint(self):
        """Test endpoint lấy tóm tắt đơn hàng."""
        # Gọi API
        url = reverse('api:orders-summary', args=[self.order1.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra dữ liệu tóm tắt
        self.assertIn('order', response.data['data'])
        self.assertIn('shipping_address', response.data['data'])
        self.assertIn('payment_method', response.data['data'])
        self.assertEqual(response.data['data']['order']['order_number'], 'ORD-001')
        self.assertEqual(response.data['data']['order']['total'], '125.00')
    
    def test_create_from_cart_endpoint(self):
        """Test endpoint tạo đơn hàng từ giỏ hàng."""
        # Skip nếu không có module Cart
        if isinstance(Cart, type) and Cart.__name__ == 'Cart':
            self.skipTest("Cart module not available")
        
        # Chuẩn bị dữ liệu
        order_data = {
            'shipping_address_id': self.shipping_address.id,
            'payment_method_id': self.payment_method.id,
            'notes': 'Order from cart'
        }
        
        # Gọi API
        url = reverse('api:orders-create-from-cart')
        response = self.client.post(url, order_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        
        # Kiểm tra đơn hàng đã được tạo
        self.assertIn('order', response.data['data'])
        self.assertEqual(response.data['data']['order']['order_status']['name'], 'Pending')


class OrderItemViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for OrderItemViewSet.
    """
    
    model_class = OrderItem
    serializer_class = OrderItemSerializer
    base_url_name = 'order-items'
    
    def setUp(self):
        """Set up specific test data for OrderItem."""
        super().setUp()
        
        # Tạo trạng thái đơn hàng
        self.status_pending = OrderStatus.objects.create(
            name='Pending',
            description='Order has been placed but not yet processed',
            color='#FFC107',
            is_active=True,
            sort_order=1
        )
        
        # Tạo địa chỉ giao hàng
        self.shipping_address = ShippingAddress.objects.create(
            user=self.users['regular'],
            recipient_name='John Doe',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            phone='1234567890',
            is_default=True
        )
        
        # Tạo phương thức thanh toán
        self.payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            code='credit_card',
            description='Pay with credit card',
            is_active=True
        )
        
        # Tạo đơn hàng
        self.order = Order.objects.create(
            user=self.users['regular'],
            order_number='ORD-001',
            order_status=self.status_pending,
            shipping_address=self.shipping_address,
            payment_method=self.payment_method,
            order_date=timezone.now(),
            shipping_cost=Decimal('10.00'),
            tax_amount=Decimal('20.00'),
            discount_amount=Decimal('5.00'),
            subtotal=Decimal('100.00'),
            total=Decimal('125.00')
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'order_id': self.order.id,
            'product_name': 'Test Product',
            'sku': 'TEST-SKU',
            'quantity': 2,
            'unit_price': '50.00',
            'subtotal': '100.00',
            'product_id': 1  # Sẽ bị bỏ qua nếu không có sản phẩm thực tế
        }
        
        self.valid_update_data = {
            'quantity': 3,
            'subtotal': '150.00'
        }
        
        # Tạo order item
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            product_name='Product 1',
            sku='SKU-001',
            quantity=2,
            unit_price=Decimal('50.00'),
            subtotal=Decimal('100.00')
        )
        
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product_name='Product 2',
            sku='SKU-002',
            quantity=1,
            unit_price=Decimal('25.00'),
            subtotal=Decimal('25.00')
        )
    
    def test_filter_by_order(self):
        """Test lọc mục đơn hàng theo đơn hàng."""
        # Tạo đơn hàng khác
        order2 = Order.objects.create(
            user=self.users['regular'],
            order_number='ORD-002',
            order_status=self.status_pending,
            shipping_address=self.shipping_address,
            payment_method=self.payment_method,
            order_date=timezone.now(),
            shipping_cost=Decimal('10.00'),
            tax_amount=Decimal('15.00'),
            discount_amount=Decimal('0.00'),
            subtotal=Decimal('75.00'),
            total=Decimal('100.00')
        )
        
        # Tạo order item cho đơn hàng khác
        order_item3 = OrderItem.objects.create(
            order=order2,
            product_name='Product 3',
            sku='SKU-003',
            quantity=3,
            unit_price=Decimal('25.00'),
            subtotal=Decimal('75.00')
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?order_id={self.order.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về mục đơn hàng của đơn hàng 1
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra tên sản phẩm
        product_names = [item['product_name'] for item in response.data['data']]
        self.assertIn('Product 1', product_names)
        self.assertIn('Product 2', product_names)
        self.assertNotIn('Product 3', product_names)
    
    def test_search_by_product_name_or_sku(self):
        """Test tìm kiếm mục đơn hàng theo tên sản phẩm hoặc SKU."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=SKU-001")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về mục đơn hàng có SKU-001
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'SKU-001')
    
    def test_update_quantity_endpoint(self):
        """Test endpoint cập nhật số lượng mục đơn hàng."""
        # Chuẩn bị dữ liệu
        quantity_data = {
            'quantity': 4,
            'subtotal': '200.00'
        }
        
        # Gọi API
        url = reverse('api:order-items-update-quantity', args=[self.order_item1.id])
        response = self.client.post(url, quantity_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng đã được cập nhật
        self.order_item1.refresh_from_db()
        self.assertEqual(self.order_item1.quantity, 4)
        self.assertEqual(self.order_item1.subtotal, Decimal('200.00'))
