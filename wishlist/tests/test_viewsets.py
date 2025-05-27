"""
Unit tests for Wishlist ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Wishlist,
bao gồm WishlistViewSet và WishlistItemViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from ..models import Wishlist, WishlistItem
try:
    from products.models import Product, Category
except ImportError:
    # Mock cho mục đích kiểm thử
    Product = type('Product', (), {})
    Category = type('Category', (), {})

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class WishlistViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for WishlistViewSet.
    """
    
    model_class = Wishlist
    # Giả sử tên serializer
    serializer_class = 'WishlistSerializer'
    base_url_name = 'wishlists'
    
    def setUp(self):
        """Set up specific test data for Wishlist."""
        super().setUp()
        
        # Tạo danh sách yêu thích cho user
        self.wishlist = Wishlist.objects.create(
            user=self.users['regular'],
            name='My Wishlist',
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
            
            # Tạo wishlist item
            self.wishlist_item1 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product1,
                added_at=timezone.now()
            )
            
            self.wishlist_item2 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product2,
                added_at=timezone.now()
            )
        else:
            # Mock wishlist items cho trường hợp không có Product model
            self.wishlist_item1 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product_id=1,
                added_at=timezone.now()
            )
            
            self.wishlist_item2 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product_id=2,
                added_at=timezone.now()
            )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'name': 'New Wishlist',
            'description': 'My new wishlist'
        }
        
        self.valid_update_data = {
            'name': 'Updated Wishlist',
            'description': 'Updated description'
        }
    
    def test_get_current_user_wishlists(self):
        """Test lấy danh sách yêu thích của user hiện tại."""
        # Gọi API
        url = reverse('api:wishlists-my-wishlists')
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng danh sách yêu thích
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'My Wishlist')
    
    def test_get_wishlist_items(self):
        """Test lấy các mục trong danh sách yêu thích."""
        # Gọi API
        url = reverse('api:wishlists-items', args=[self.wishlist.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng mục
        self.assertEqual(len(response.data['data']), 2)
    
    def test_add_item_to_wishlist(self):
        """Test thêm mục vào danh sách yêu thích."""
        # Chuẩn bị dữ liệu
        item_data = {
            'product_id': 3  # Giả sử ID sản phẩm mới
        }
        
        # Gọi API
        url = reverse('api:wishlists-add-item', args=[self.wishlist.id])
        response = self.client.post(url, item_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        
        # Kiểm tra mục đã được thêm vào danh sách yêu thích
        wishlist_items = WishlistItem.objects.filter(wishlist=self.wishlist)
        self.assertEqual(wishlist_items.count(), 3)
    
    def test_remove_item_from_wishlist(self):
        """Test xóa mục khỏi danh sách yêu thích."""
        # Gọi API
        url = reverse('api:wishlists-remove-item', args=[self.wishlist.id, self.wishlist_item1.id])
        response = self.client.delete(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra mục đã bị xóa
        wishlist_items = WishlistItem.objects.filter(wishlist=self.wishlist)
        self.assertEqual(wishlist_items.count(), 1)
        
        # Kiểm tra mục không còn tồn tại
        with self.assertRaises(WishlistItem.DoesNotExist):
            self.wishlist_item1.refresh_from_db()
    
    def test_clear_wishlist(self):
        """Test xóa tất cả mục khỏi danh sách yêu thích."""
        # Gọi API
        url = reverse('api:wishlists-clear', args=[self.wishlist.id])
        response = self.client.post(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_204_NO_CONTENT)
        
        # Kiểm tra tất cả mục đã bị xóa
        wishlist_items = WishlistItem.objects.filter(wishlist=self.wishlist)
        self.assertEqual(wishlist_items.count(), 0)
    
    def test_move_to_cart(self):
        """Test chuyển mục từ danh sách yêu thích sang giỏ hàng."""
        # Skip nếu không có module Cart
        try:
            from cart.models import Cart, CartItem
        except ImportError:
            self.skipTest("Cart module not available")
        
        # Chuẩn bị dữ liệu
        item_data = {
            'wishlist_item_id': self.wishlist_item1.id,
            'quantity': 1
        }
        
        # Gọi API
        url = reverse('api:wishlists-move-to-cart', args=[self.wishlist.id])
        response = self.client.post(url, item_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        
        # Kiểm tra mục đã được thêm vào giỏ hàng
        self.assertIn('cart_item', response.data['data'])
        
        # Kiểm tra mục đã bị xóa khỏi danh sách yêu thích
        with self.assertRaises(WishlistItem.DoesNotExist):
            self.wishlist_item1.refresh_from_db()


class WishlistItemViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for WishlistItemViewSet.
    """
    
    model_class = WishlistItem
    # Giả sử tên serializer
    serializer_class = 'WishlistItemSerializer'
    base_url_name = 'wishlist-items'
    
    def setUp(self):
        """Set up specific test data for WishlistItem."""
        super().setUp()
        
        # Tạo danh sách yêu thích cho user
        self.wishlist = Wishlist.objects.create(
            user=self.users['regular'],
            name='My Wishlist',
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
                'wishlist_id': self.wishlist.id,
                'product_id': self.product1.id
            }
            
            # Tạo wishlist item
            self.wishlist_item1 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product1,
                added_at=timezone.now()
            )
            
            self.wishlist_item2 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product2,
                added_at=timezone.now()
            )
        else:
            # Mock dữ liệu cho trường hợp không có Product model
            self.valid_create_data = {
                'wishlist_id': self.wishlist.id,
                'product_id': 1
            }
            
            # Mock wishlist items
            self.wishlist_item1 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product_id=1,
                added_at=timezone.now()
            )
            
            self.wishlist_item2 = WishlistItem.objects.create(
                wishlist=self.wishlist,
                product_id=2,
                added_at=timezone.now()
            )
    
    def test_filter_by_wishlist(self):
        """Test lọc mục theo danh sách yêu thích."""
        # Tạo danh sách yêu thích khác
        wishlist2 = Wishlist.objects.create(
            user=self.users['admin'],
            name='Admin Wishlist',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Tạo wishlist item cho danh sách yêu thích khác
        wishlist_item3 = WishlistItem.objects.create(
            wishlist=wishlist2,
            product_id=3,  # Giả sử ID sản phẩm mới
            added_at=timezone.now()
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?wishlist_id={self.wishlist.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về mục của danh sách yêu thích 1
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra product IDs
        product_ids = [item['product_id'] for item in response.data['data']]
        self.assertTrue(1 in product_ids or self.product1.id in product_ids)
        self.assertTrue(2 in product_ids or self.product2.id in product_ids)
        self.assertFalse(3 in product_ids)
    
    def test_check_product_in_wishlist(self):
        """Test kiểm tra sản phẩm có trong danh sách yêu thích không."""
        # Gọi API
        product_id = 1  # Hoặc self.product1.id nếu có thực sự
        url = reverse('api:wishlist-items-check-product', args=[product_id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra kết quả
        self.assertTrue(response.data['data']['in_wishlist'])
        self.assertEqual(response.data['data']['wishlist_item_id'], self.wishlist_item1.id)
    
    def test_bulk_add_to_wishlist(self):
        """Test thêm nhiều sản phẩm vào danh sách yêu thích cùng lúc."""
        # Chuẩn bị dữ liệu
        bulk_data = {
            'wishlist_id': self.wishlist.id,
            'product_ids': [3, 4, 5]  # Giả sử ID sản phẩm mới
        }
        
        # Gọi API
        url = reverse('api:wishlist-items-bulk-add')
        response = self.client.post(url, bulk_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_201_CREATED)
        
        # Kiểm tra số lượng mục đã thêm
        self.assertIn('items_added', response.data['data'])
        self.assertEqual(response.data['data']['items_added'], 3)
        
        # Kiểm tra tổng số mục trong danh sách yêu thích
        wishlist_items = WishlistItem.objects.filter(wishlist=self.wishlist)
        self.assertEqual(wishlist_items.count(), 5)  # 2 cũ + 3 mới
