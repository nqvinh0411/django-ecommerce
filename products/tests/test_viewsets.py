"""
Unit tests for Products ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Products,
bao gồm ProductViewSet, CategoryViewSet, BrandViewSet, và ProductVariantViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from ..models import Product, Category, Brand, ProductVariant, ProductAttribute, ProductImage
from ..serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer, 
    ProductVariantSerializer, ProductAttributeSerializer, ProductImageSerializer
)

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class CategoryViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for CategoryViewSet.
    """
    
    model_class = Category
    serializer_class = CategorySerializer
    base_url_name = 'categories'
    
    valid_create_data = {
        'name': 'Test Category',
        'slug': 'test-category',
        'description': 'This is a test category',
        'is_active': True
    }
    
    valid_update_data = {
        'name': 'Updated Category',
        'description': 'This is an updated category description'
    }
    
    def setUp(self):
        """Set up specific test data for Category."""
        super().setUp()
        
        # Tạo category
        self.parent_category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic products',
            is_active=True,
            parent=None
        )
        
        self.sub_category = Category.objects.create(
            name='Smartphones',
            slug='smartphones',
            description='Smartphone products',
            is_active=True,
            parent=self.parent_category
        )
        
        self.inactive_category = Category.objects.create(
            name='Inactive Category',
            slug='inactive-category',
            description='This category is inactive',
            is_active=False,
            parent=None
        )
    
    def test_filter_by_is_active(self):
        """Test lọc danh mục theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về danh mục đang hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra danh mục không hoạt động không được trả về
        category_names = [cat['name'] for cat in response.data['data']]
        self.assertNotIn('Inactive Category', category_names)
    
    def test_filter_by_parent(self):
        """Test lọc danh mục theo danh mục cha."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?parent_id={self.parent_category.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về danh mục con của Electronics
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Smartphones')
    
    def test_get_root_categories(self):
        """Test lấy danh mục gốc."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_root=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về danh mục gốc
        self.assertEqual(len(response.data['data']), 2)  # Electronics và Inactive Category
        
        # Kiểm tra danh mục con không được trả về
        category_names = [cat['name'] for cat in response.data['data']]
        self.assertNotIn('Smartphones', category_names)
    
    def test_get_category_products(self):
        """Test lấy sản phẩm trong danh mục."""
        # Tạo brand
        brand = Brand.objects.create(
            name='Test Brand',
            slug='test-brand',
            description='Test brand description'
        )
        
        # Tạo sản phẩm trong danh mục con
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test product description',
            price=Decimal('99.99'),
            category=self.sub_category,
            brand=brand,
            is_active=True
        )
        
        # Gọi API
        url = reverse('api:categories-products', args=[self.sub_category.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách sản phẩm
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Test Product')


class BrandViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for BrandViewSet.
    """
    
    model_class = Brand
    serializer_class = BrandSerializer
    base_url_name = 'brands'
    
    valid_create_data = {
        'name': 'Test Brand',
        'slug': 'test-brand',
        'description': 'This is a test brand',
        'logo_url': 'https://example.com/logo.png',
        'website': 'https://example.com'
    }
    
    valid_update_data = {
        'name': 'Updated Brand',
        'description': 'This is an updated brand description'
    }
    
    def setUp(self):
        """Set up specific test data for Brand."""
        super().setUp()
        
        # Tạo brand
        self.brand1 = Brand.objects.create(
            name='Apple',
            slug='apple',
            description='Apple Inc.',
            logo_url='https://example.com/apple.png',
            website='https://apple.com'
        )
        
        self.brand2 = Brand.objects.create(
            name='Samsung',
            slug='samsung',
            description='Samsung Electronics',
            logo_url='https://example.com/samsung.png',
            website='https://samsung.com'
        )
    
    def test_search_by_name(self):
        """Test tìm kiếm thương hiệu theo tên."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=app")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về thương hiệu có 'app' trong tên
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Apple')
    
    def test_get_brand_products(self):
        """Test lấy sản phẩm của thương hiệu."""
        # Tạo danh mục
        category = Category.objects.create(
            name='Smartphones',
            slug='smartphones',
            description='Smartphone products',
            is_active=True
        )
        
        # Tạo sản phẩm của thương hiệu
        product = Product.objects.create(
            name='iPhone 14',
            slug='iphone-14',
            description='Latest iPhone',
            price=Decimal('999.99'),
            category=category,
            brand=self.brand1,
            is_active=True
        )
        
        # Gọi API
        url = reverse('api:brands-products', args=[self.brand1.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách sản phẩm
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'iPhone 14')


class ProductViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for ProductViewSet.
    """
    
    model_class = Product
    serializer_class = ProductSerializer
    base_url_name = 'products'
    
    def setUp(self):
        """Set up specific test data for Product."""
        super().setUp()
        
        # Tạo danh mục
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic products',
            is_active=True
        )
        
        # Tạo thương hiệu
        self.brand = Brand.objects.create(
            name='Apple',
            slug='apple',
            description='Apple Inc.',
            logo_url='https://example.com/apple.png',
            website='https://apple.com'
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'This is a test product',
            'price': '99.99',
            'category_id': self.category.id,
            'brand_id': self.brand.id,
            'is_active': True,
            'stock_quantity': 100,
            'weight': 0.5,
            'dimensions': '10x5x2'
        }
        
        self.valid_update_data = {
            'name': 'Updated Product',
            'description': 'This is an updated product description',
            'price': '129.99'
        }
        
        # Tạo sản phẩm
        self.product1 = Product.objects.create(
            name='iPhone 14',
            slug='iphone-14',
            description='Latest iPhone',
            price=Decimal('999.99'),
            category=self.category,
            brand=self.brand,
            is_active=True,
            stock_quantity=50,
            weight=0.2,
            dimensions='15x7x0.8'
        )
        
        self.product2 = Product.objects.create(
            name='MacBook Pro',
            slug='macbook-pro',
            description='Powerful laptop',
            price=Decimal('1999.99'),
            category=self.category,
            brand=self.brand,
            is_active=True,
            stock_quantity=20,
            weight=1.5,
            dimensions='30x20x1.5'
        )
        
        self.inactive_product = Product.objects.create(
            name='Inactive Product',
            slug='inactive-product',
            description='This product is inactive',
            price=Decimal('499.99'),
            category=self.category,
            brand=self.brand,
            is_active=False,
            stock_quantity=0
        )
    
    def test_filter_by_is_active(self):
        """Test lọc sản phẩm theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về sản phẩm đang hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra sản phẩm không hoạt động không được trả về
        product_names = [prod['name'] for prod in response.data['data']]
        self.assertNotIn('Inactive Product', product_names)
    
    def test_filter_by_category(self):
        """Test lọc sản phẩm theo danh mục."""
        # Tạo danh mục khác
        category2 = Category.objects.create(
            name='Accessories',
            slug='accessories',
            description='Accessories products',
            is_active=True
        )
        
        # Tạo sản phẩm trong danh mục khác
        product3 = Product.objects.create(
            name='AirPods',
            slug='airpods',
            description='Wireless earbuds',
            price=Decimal('199.99'),
            category=category2,
            brand=self.brand,
            is_active=True,
            stock_quantity=100
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?category_id={self.category.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về sản phẩm trong danh mục Electronics
        self.assertEqual(len(response.data['data']), 3)  # 2 active + 1 inactive
        
        # Kiểm tra sản phẩm từ danh mục khác không được trả về
        product_names = [prod['name'] for prod in response.data['data']]
        self.assertNotIn('AirPods', product_names)
    
    def test_filter_by_brand(self):
        """Test lọc sản phẩm theo thương hiệu."""
        # Tạo thương hiệu khác
        brand2 = Brand.objects.create(
            name='Samsung',
            slug='samsung',
            description='Samsung Electronics',
            logo_url='https://example.com/samsung.png',
            website='https://samsung.com'
        )
        
        # Tạo sản phẩm của thương hiệu khác
        product3 = Product.objects.create(
            name='Galaxy S23',
            slug='galaxy-s23',
            description='Latest Galaxy',
            price=Decimal('899.99'),
            category=self.category,
            brand=brand2,
            is_active=True,
            stock_quantity=40
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?brand_id={self.brand.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về sản phẩm của thương hiệu Apple
        self.assertEqual(len(response.data['data']), 3)  # 2 active + 1 inactive
        
        # Kiểm tra sản phẩm của thương hiệu khác không được trả về
        product_names = [prod['name'] for prod in response.data['data']]
        self.assertNotIn('Galaxy S23', product_names)
    
    def test_filter_by_price_range(self):
        """Test lọc sản phẩm theo khoảng giá."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?min_price=1000&max_price=2500")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về sản phẩm trong khoảng giá 1000-2500
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'MacBook Pro')
    
    def test_search_products(self):
        """Test tìm kiếm sản phẩm."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=iphone")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về sản phẩm có 'iphone' trong tên hoặc mô tả
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'iPhone 14')
    
    def test_product_variants_endpoint(self):
        """Test endpoint lấy biến thể sản phẩm."""
        # Tạo biến thể sản phẩm
        variant = ProductVariant.objects.create(
            product=self.product1,
            sku='IP14-BLK-128',
            price_adjustment=Decimal('0.00'),
            stock_quantity=30,
            color='Black',
            size='128GB',
            is_active=True
        )
        
        # Gọi API
        url = reverse('api:products-variants', args=[self.product1.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách biến thể
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'IP14-BLK-128')
    
    def test_product_images_endpoint(self):
        """Test endpoint lấy hình ảnh sản phẩm."""
        # Tạo hình ảnh sản phẩm
        image = ProductImage.objects.create(
            product=self.product1,
            image_url='https://example.com/iphone14.jpg',
            alt_text='iPhone 14 Image',
            is_primary=True,
            sort_order=1
        )
        
        # Gọi API
        url = reverse('api:products-images', args=[self.product1.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra danh sách hình ảnh
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['image_url'], 'https://example.com/iphone14.jpg')


class ProductVariantViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for ProductVariantViewSet.
    """
    
    model_class = ProductVariant
    serializer_class = ProductVariantSerializer
    base_url_name = 'product-variants'
    
    def setUp(self):
        """Set up specific test data for ProductVariant."""
        super().setUp()
        
        # Tạo danh mục
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic products',
            is_active=True
        )
        
        # Tạo thương hiệu
        self.brand = Brand.objects.create(
            name='Apple',
            slug='apple',
            description='Apple Inc.'
        )
        
        # Tạo sản phẩm
        self.product = Product.objects.create(
            name='iPhone 14',
            slug='iphone-14',
            description='Latest iPhone',
            price=Decimal('999.99'),
            category=self.category,
            brand=self.brand,
            is_active=True,
            stock_quantity=100
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'product_id': self.product.id,
            'sku': 'IP14-RED-128',
            'price_adjustment': '50.00',
            'stock_quantity': 20,
            'color': 'Red',
            'size': '128GB',
            'is_active': True
        }
        
        self.valid_update_data = {
            'price_adjustment': '75.00',
            'stock_quantity': 15
        }
        
        # Tạo biến thể sản phẩm
        self.variant1 = ProductVariant.objects.create(
            product=self.product,
            sku='IP14-BLK-128',
            price_adjustment=Decimal('0.00'),
            stock_quantity=30,
            color='Black',
            size='128GB',
            is_active=True
        )
        
        self.variant2 = ProductVariant.objects.create(
            product=self.product,
            sku='IP14-BLU-256',
            price_adjustment=Decimal('100.00'),
            stock_quantity=20,
            color='Blue',
            size='256GB',
            is_active=True
        )
        
        self.inactive_variant = ProductVariant.objects.create(
            product=self.product,
            sku='IP14-GRY-512',
            price_adjustment=Decimal('200.00'),
            stock_quantity=0,
            color='Gray',
            size='512GB',
            is_active=False
        )
    
    def test_filter_by_product(self):
        """Test lọc biến thể theo sản phẩm."""
        # Tạo sản phẩm khác
        product2 = Product.objects.create(
            name='iPhone 13',
            slug='iphone-13',
            description='Previous iPhone',
            price=Decimal('799.99'),
            category=self.category,
            brand=self.brand,
            is_active=True
        )
        
        # Tạo biến thể cho sản phẩm khác
        variant3 = ProductVariant.objects.create(
            product=product2,
            sku='IP13-BLK-128',
            price_adjustment=Decimal('0.00'),
            stock_quantity=50,
            color='Black',
            size='128GB',
            is_active=True
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?product_id={self.product.id}")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về biến thể của iPhone 14
        self.assertEqual(len(response.data['data']), 3)  # 2 active + 1 inactive
        
        # Kiểm tra biến thể của sản phẩm khác không được trả về
        variant_skus = [var['sku'] for var in response.data['data']]
        self.assertNotIn('IP13-BLK-128', variant_skus)
    
    def test_filter_by_is_active(self):
        """Test lọc biến thể theo trạng thái active."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về biến thể đang hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra biến thể không hoạt động không được trả về
        variant_skus = [var['sku'] for var in response.data['data']]
        self.assertNotIn('IP14-GRY-512', variant_skus)
    
    def test_filter_by_color_and_size(self):
        """Test lọc biến thể theo màu sắc và kích thước."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?color=Black&size=128GB")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về biến thể màu đen, kích thước 128GB
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'IP14-BLK-128')
    
    def test_update_stock_endpoint(self):
        """Test endpoint cập nhật tồn kho."""
        # Chuẩn bị dữ liệu
        stock_data = {
            'stock_quantity': 25,
            'reason': 'Stock adjustment'
        }
        
        # Gọi API
        url = reverse('api:product-variants-update-stock', args=[self.variant1.id])
        response = self.client.post(url, stock_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng tồn kho đã được cập nhật
        self.variant1.refresh_from_db()
        self.assertEqual(self.variant1.stock_quantity, 25)
