"""
Unit tests for Cart ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Cart,
bao gồm CartViewSet và CartItemViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from ..models import Cart, CartItem
try:
    from products.models import Product, Category
except ImportError:
    # Mock cho mục đích kiểm thử
    Product = type('Product', (), {})
    Category = type('Category', (), {})

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class CartViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for CartViewSet.
    """
    
    model_class = Cart
    # Giả sử tên serializer
    serializer_class = 'CartSerializer'  
    base_url_name = 'carts'
    
    def setUp(self):
        """Set up specific test data for Cart."""
        super().setUp()
        
        # Tạo giỏ hàng cho user
        self.cart = Cart.objects.create(
            user=self.users['regular'],
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Nếu Product là một class thực sự (không phải mock)
        if not isinstance(Product, type) or Product.__name__ != 'Product':
            # Tạo category
            self.category = Category.objects.create(
                name='Test Category',
                slug='test-category',
                description='Test category description'
            )
            
            # Tạo sản phẩm
            self.product1 = Product.objects.create(
                name='Product 1',
                price=Decimal('50.00'),
                category=self.category
            )
            
            self.product2 = Product.objects.create(
                name='Product 2',
                price=Decimal('25.00'),
                category=self.category
            )
            
            # Tạo cart item
            self.cart_item1 = CartItem.objects.create(
                cart=self.cart,
                product=self.product1,
                quantity=2,
                price=Decimal('50.00')
            )
            
            self.cart_item2 = CartItem.objects.create(
                cart=self.cart,
                product=self.product2,
                quantity=1,
                price=Decimal('25.00')
            )
        else:
            # Mock cart items cho trường hợp không có Product model
            self.cart_item1 = CartItem.objects.create(
                cart=self.cart,
                product_id=1,
                quantity=2,
                price=Decimal('50.00')
            )
            
            self.cart_item2 = CartItem.objects.create(
                cart=self.cart,
                product_id=2,
                quantity=1,
                price=Decimal('25.00')
            )
    
    def test_get_current_cart(self):
        """Test lấy giỏ hàng hiện tại của user."""
        # Gọi API
        url = reverse('api:carts-current')
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra dữ liệu giỏ hàng
        self.assertIn('cart', response.data['data'])
        self.assertIn('items', response.data['data'])
        
        # Kiểm tra số lượng mục trong giỏ hàng
        self.assertEqual(len(response.data['data']['items']), 2)
    
    def test_add_item_to_cart(self):
        """Test thêm mục vào giỏ hàng."""
        # Chuẩn bị dữ liệu
        item_data = {
            'product_id': 3,  # Giả sử ID sản phẩm mới
            'quantity': 3,
            'price': '30.00'
        }
        
        # Gọi API
        url = reverse('api:carts-add-item')
        response = self.client.post(url, item_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        
        # Kiểm tra mục đã được thêm vào giỏ hàng
        self.assertIn('item', response.data['data'])
        self.assertEqual(response.data['data']['item']['quantity'], 3)
        
        # Kiểm tra số lượng mục trong giỏ hàng
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 3)
    
    def test_update_cart_item(self):
        """Test cập nhật mục trong giỏ hàng."""
        # Chuẩn bị dữ liệu
        update_data = {
            'quantity': 4
        }
        
        # Gọi API
        url = reverse('api:carts-update-item', args=[self.cart_item1.id])
        response = self.client.put(url, update_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra mục đã được cập nhật
        self.cart_item1.refresh_from_db()
        self.assertEqual(self.cart_item1.quantity, 4)
    
    def test_remove_cart_item(self):
        """Test xóa mục khỏi giỏ hàng."""
        # Gọi API
        url = reverse('api:carts-remove-item', args=[self.cart_item1.id])
        response = self.client.delete(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra mục đã bị xóa
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 1)
        
        # Kiểm tra mục không còn tồn tại
        with self.assertRaises(CartItem.DoesNotExist):
            self.cart_item1.refresh_from_db()
    
    def test_clear_cart(self):
        """Test xóa tất cả mục khỏi giỏ hàng."""
        # Gọi API
        url = reverse('api:carts-clear')
        response = self.client.post(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra tất cả mục đã bị xóa
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 0)
    
    def test_cart_summary(self):
        """Test lấy tóm tắt giỏ hàng."""
        # Gọi API
        url = reverse('api:carts-summary')
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra dữ liệu tóm tắt
        self.assertIn('item_count', response.data['data'])
        self.assertIn('subtotal', response.data['data'])
        self.assertEqual(response.data['data']['item_count'], 2)
        self.assertEqual(response.data['data']['subtotal'], '125.00')  # 2*50 + 1*25


class CartItemViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for CartItemViewSet.
    """
    
    model_class = CartItem
    # Giả sử tên serializer
    serializer_class = 'CartItemSerializer'  
    base_url_name = 'cart-items'
    
    def setUp(self):
        """Set up specific test data for CartItem."""
        super().setUp()
        
        # Tạo giỏ hàng cho user
        self.cart = Cart.objects.create(
            user=self.users['regular'],
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Nếu Product là một class thực sự (không phải mock)
        if not isinstance(Product, type) or Product.__name__ != 'Product':
            # Tạo category
            self.category = Category.objects.create(
                name='Test Category',
                slug='test-category',
                description='Test category description'
            )
            
            # Tạo sản phẩm
            self.product1 = Product.objects.create(
                name='Product 1',
                price=Decimal('50.00'),
                category=self.category
            )
            
            self.product2 = Product.objects.create(
                name='Product 2',
                price=Decimal('25.00'),
                category=self.category
            )
            
            # Thiết lập dữ liệu hợp lệ cho việc tạo
            self.valid_create_data = {
                'cart_id': self.cart.id,
                'product_id': self.product1.id,
                'quantity': 2,
                'price': '50.00'
            }
            
            # Tạo cart item
            self.cart_item1 = CartItem.objects.create(
                cart=self.cart,
                product=self.product1,
                quantity=2,
                price=Decimal('50.00')
            )
            
            self.cart_item2 = CartItem.objects.create(
                cart=self.cart,
                product=self.product2,
                quantity=1,
                price=Decimal('25.00')
            )
        else:
            # Mock dữ liệu cho trường hợp không có Product model
            self.valid_create_data = {
                'cart_id': self.cart.id,
                'product_id': 1,
                'quantity': 2,
                'price': '50.00'
            }
            
            # Mock cart items
            self.cart_item1 = CartItem.objects.create(
                cart=self.cart,
                product_id=1,
                quantity=2,
                price=Decimal('50.00')
            )
            
            self.cart_item2 = CartItem.objects.create(
                cart=self.cart,
                product_id=2,
                quantity=1,
                price=Decimal('25.00')
            )
        
        # Thiết lập dữ liệu hợp lệ cho việc cập nhật
        self.valid_update_data = {
            'quantity': 3
        }
    
    def test_filter_by_cart(self):
        """Test lọc mục giỏ hàng theo giỏ hàng."""
        # Tạo giỏ hàng khác
        cart2 = Cart.objects.create(
            user=self.users['admin'],
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Tạo cart item cho giỏ hàng khác
        cart_item3 = CartItem.objects.create(
            cart=cart2,
            product_id=3,  # Giả sử ID sản phẩm mới
            quantity=3,
            price=Decimal('30.00')
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?cart_id={self.cart.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về mục của giỏ hàng 1
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra số lượng sản phẩm
        quantities = [item['quantity'] for item in response.data['data']]
        self.assertIn(2, quantities)
        self.assertIn(1, quantities)
        self.assertNotIn(3, quantities)
    
    def test_bulk_update_endpoint(self):
        """Test endpoint cập nhật hàng loạt các mục giỏ hàng."""
        # Chuẩn bị dữ liệu
        bulk_data = {
            'items': [
                {
                    'id': self.cart_item1.id,
                    'quantity': 4
                },
                {
                    'id': self.cart_item2.id,
                    'quantity': 2
                }
            ]
        }
        
        # Gọi API
        url = reverse('api:cart-items-bulk-update')
        response = self.client.put(url, bulk_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra các mục đã được cập nhật
        self.cart_item1.refresh_from_db()
        self.cart_item2.refresh_from_db()
        self.assertEqual(self.cart_item1.quantity, 4)
        self.assertEqual(self.cart_item2.quantity, 2)
    
    def test_increment_quantity_endpoint(self):
        """Test endpoint tăng số lượng mục giỏ hàng."""
        # Số lượng ban đầu
        initial_quantity = self.cart_item1.quantity
        
        # Gọi API
        url = reverse('api:cart-items-increment', args=[self.cart_item1.id])
        response = self.client.post(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng đã tăng
        self.cart_item1.refresh_from_db()
        self.assertEqual(self.cart_item1.quantity, initial_quantity + 1)
    
    def test_decrement_quantity_endpoint(self):
        """Test endpoint giảm số lượng mục giỏ hàng."""
        # Số lượng ban đầu
        initial_quantity = self.cart_item1.quantity
        
        # Gọi API
        url = reverse('api:cart-items-decrement', args=[self.cart_item1.id])
        response = self.client.post(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng đã giảm
        self.cart_item1.refresh_from_db()
        self.assertEqual(self.cart_item1.quantity, initial_quantity - 1)
    
    def test_decrement_to_zero_removes_item(self):
        """Test giảm số lượng xuống 0 sẽ xóa mục khỏi giỏ hàng."""
        # Đặt số lượng mục thành 1
        self.cart_item2.quantity = 1
        self.cart_item2.save()
        
        # Gọi API
        url = reverse('api:cart-items-decrement', args=[self.cart_item2.id])
        response = self.client.post(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra mục đã bị xóa
        with self.assertRaises(CartItem.DoesNotExist):
            self.cart_item2.refresh_from_db()
