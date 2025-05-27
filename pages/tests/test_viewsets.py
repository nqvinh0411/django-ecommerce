"""
Unit tests for Pages ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Pages,
bao gồm PageViewSet, BannerViewSet, MenuViewSet và ContentBlockViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Page, Banner, Menu, MenuItem, ContentBlock
from ..serializers import (
    PageSerializer, BannerSerializer, 
    MenuSerializer, MenuItemSerializer, ContentBlockSerializer
)

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class PageViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for PageViewSet.
    """
    
    model_class = Page
    serializer_class = PageSerializer
    base_url_name = 'pages'
    
    valid_create_data = {
        'title': 'Test Page',
        'slug': 'test-page',
        'content': '<p>This is a test page content.</p>',
        'meta_title': 'Test Page | E-commerce',
        'meta_description': 'This is a test page for our e-commerce system',
        'is_active': True,
        'layout': 'standard'
    }
    
    valid_update_data = {
        'title': 'Updated Test Page',
        'content': '<p>This is updated content.</p>',
        'meta_title': 'Updated Test Page | E-commerce'
    }
    
    def setUp(self):
        """Set up specific test data for Page."""
        super().setUp()
        
        # Tạo một số trang cho test
        self.home_page = Page.objects.create(
            title='Home Page',
            slug='home',
            content='<p>Welcome to our e-commerce store!</p>',
            meta_title='Home | E-commerce Store',
            meta_description='Welcome to our e-commerce store',
            is_active=True,
            layout='home',
            is_homepage=True
        )
        
        self.about_page = Page.objects.create(
            title='About Us',
            slug='about-us',
            content='<p>Learn about our company.</p>',
            meta_title='About Us | E-commerce Store',
            meta_description='Learn about our company and our mission',
            is_active=True,
            layout='standard',
            is_homepage=False
        )
    
    def test_filter_by_is_active(self):
        """Test lọc trang theo trạng thái active."""
        # Đặt about_page thành không hoạt động
        self.about_page.is_active = False
        self.about_page.save()
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về trang đang hoạt động
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Home Page')
    
    def test_get_by_slug(self):
        """Test lấy trang theo slug."""
        # Gọi API với parameter slug
        response = self.client.get(f"{self.list_url}?slug=home")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về trang có slug phù hợp
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['slug'], 'home')
    
    def test_set_homepage(self):
        """Test thiết lập trang chủ."""
        # Chuẩn bị dữ liệu
        homepage_data = {
            'is_homepage': True
        }
        
        # Gọi API
        url = self.get_detail_url(self.about_page.id)
        response = self.client.patch(url, homepage_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra trang about đã được đặt làm trang chủ
        self.about_page.refresh_from_db()
        self.home_page.refresh_from_db()
        
        self.assertEqual(self.about_page.is_homepage, True)
        self.assertEqual(self.home_page.is_homepage, False)  # Trang cũ không còn là trang chủ
    
    def test_search_pages(self):
        """Test tìm kiếm trang."""
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=about")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về trang có 'about' trong tiêu đề hoặc nội dung
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'About Us')


class BannerViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for BannerViewSet.
    """
    
    model_class = Banner
    serializer_class = BannerSerializer
    base_url_name = 'banners'
    
    valid_create_data = {
        'title': 'Test Banner',
        'subtitle': 'Welcome to our store',
        'image_url': 'https://example.com/banner.jpg',
        'link': '/products',
        'position': 'home_top',
        'start_date': timezone.now().isoformat(),
        'end_date': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        'is_active': True,
        'priority': 1
    }
    
    valid_update_data = {
        'title': 'Updated Banner',
        'subtitle': 'Special offers inside',
        'priority': 2
    }
    
    def setUp(self):
        """Set up specific test data for Banner."""
        super().setUp()
        
        # Tạo banner
        self.banner1 = Banner.objects.create(
            title='Summer Sale',
            subtitle='Up to 50% off',
            image_url='https://example.com/summer-sale.jpg',
            link='/sales/summer',
            position='home_top',
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=20),
            is_active=True,
            priority=1
        )
        
        self.banner2 = Banner.objects.create(
            title='New Arrivals',
            subtitle='Check out our latest products',
            image_url='https://example.com/new-arrivals.jpg',
            link='/new-arrivals',
            position='home_middle',
            start_date=timezone.now() - timezone.timedelta(days=5),
            end_date=timezone.now() + timezone.timedelta(days=25),
            is_active=True,
            priority=2
        )
    
    def test_filter_by_position(self):
        """Test lọc banner theo vị trí."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?position=home_top")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về banner ở vị trí home_top
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Summer Sale')
    
    def test_filter_by_active_date_range(self):
        """Test lọc banner theo khoảng thời gian hoạt động."""
        # Tạo banner hết hạn
        expired_banner = Banner.objects.create(
            title='Expired Banner',
            subtitle='This banner has expired',
            image_url='https://example.com/expired.jpg',
            link='/expired',
            position='home_bottom',
            start_date=timezone.now() - timezone.timedelta(days=60),
            end_date=timezone.now() - timezone.timedelta(days=30),
            is_active=True,
            priority=3
        )
        
        # Gọi API với filter active=true (chỉ lấy banner trong khoảng thời gian hoạt động)
        response = self.client.get(f"{self.list_url}?active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về banner đang trong khoảng thời gian hoạt động
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra banner hết hạn không được trả về
        banner_titles = [banner['title'] for banner in response.data['data']]
        self.assertNotIn('Expired Banner', banner_titles)
    
    def test_order_by_priority(self):
        """Test sắp xếp banner theo ưu tiên."""
        # Gọi API với sắp xếp
        response = self.client.get(f"{self.list_url}?ordering=priority")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra thứ tự banner theo priority tăng dần
        self.assertEqual(response.data['data'][0]['title'], 'Summer Sale')  # priority=1
        self.assertEqual(response.data['data'][1]['title'], 'New Arrivals')  # priority=2


class MenuViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for MenuViewSet.
    """
    
    model_class = Menu
    serializer_class = MenuSerializer
    base_url_name = 'menus'
    
    valid_create_data = {
        'name': 'Test Menu',
        'location': 'header',
        'is_active': True
    }
    
    valid_update_data = {
        'name': 'Updated Menu',
        'location': 'footer'
    }
    
    def setUp(self):
        """Set up specific test data for Menu."""
        super().setUp()
        
        # Tạo menu
        self.header_menu = Menu.objects.create(
            name='Header Menu',
            location='header',
            is_active=True
        )
        
        self.footer_menu = Menu.objects.create(
            name='Footer Menu',
            location='footer',
            is_active=True
        )
        
        # Tạo menu items
        self.home_item = MenuItem.objects.create(
            menu=self.header_menu,
            parent=None,
            title='Home',
            url='/',
            order=1,
            is_active=True
        )
        
        self.products_item = MenuItem.objects.create(
            menu=self.header_menu,
            parent=None,
            title='Products',
            url='/products',
            order=2,
            is_active=True
        )
        
        # Tạo menu item con
        self.new_arrivals_item = MenuItem.objects.create(
            menu=self.header_menu,
            parent=self.products_item,
            title='New Arrivals',
            url='/products/new-arrivals',
            order=1,
            is_active=True
        )
    
    def test_filter_by_location(self):
        """Test lọc menu theo vị trí."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?location=header")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về menu ở vị trí header
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Header Menu')
    
    def test_get_menu_items(self):
        """Test lấy các menu items của một menu."""
        # Gọi API
        url = reverse('api:menus-items', args=[self.header_menu.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra số lượng menu items
        self.assertEqual(len(response.data['data']), 2)  # 2 items cấp cao nhất
        
        # Kiểm tra menu item con
        products_item = next(item for item in response.data['data'] if item['title'] == 'Products')
        self.assertEqual(len(products_item['children']), 1)
        self.assertEqual(products_item['children'][0]['title'], 'New Arrivals')
    
    def test_reorder_menu_items(self):
        """Test sắp xếp lại các menu items."""
        # Chuẩn bị dữ liệu
        reorder_data = {
            'item_orders': [
                {'id': self.products_item.id, 'order': 1},
                {'id': self.home_item.id, 'order': 2}
            ]
        }
        
        # Gọi API
        url = reverse('api:menus-reorder-items', args=[self.header_menu.id])
        response = self.client.post(url, reorder_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra thứ tự đã được cập nhật
        self.products_item.refresh_from_db()
        self.home_item.refresh_from_db()
        
        self.assertEqual(self.products_item.order, 1)
        self.assertEqual(self.home_item.order, 2)


class ContentBlockViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for ContentBlockViewSet.
    """
    
    model_class = ContentBlock
    serializer_class = ContentBlockSerializer
    base_url_name = 'content-blocks'
    
    valid_create_data = {
        'title': 'Test Block',
        'identifier': 'test_block',
        'content': '<p>This is a test content block.</p>',
        'content_type': 'html',
        'location': 'home_featured',
        'is_active': True
    }
    
    valid_update_data = {
        'title': 'Updated Block',
        'content': '<p>This is updated content.</p>'
    }
    
    def setUp(self):
        """Set up specific test data for ContentBlock."""
        super().setUp()
        
        # Tạo content blocks
        self.featured_block = ContentBlock.objects.create(
            title='Featured Products',
            identifier='featured_products',
            content='<p>Check out our featured products!</p>',
            content_type='html',
            location='home_featured',
            is_active=True
        )
        
        self.about_block = ContentBlock.objects.create(
            title='About Us Block',
            identifier='about_us_block',
            content='<p>Learn about our company history.</p>',
            content_type='html',
            location='about_page',
            is_active=True
        )
        
        self.json_block = ContentBlock.objects.create(
            title='Features Block',
            identifier='features_block',
            content='{"features": ["Fast Shipping", "24/7 Support", "Easy Returns"]}',
            content_type='json',
            location='home_features',
            is_active=True
        )
    
    def test_filter_by_content_type(self):
        """Test lọc content blocks theo loại nội dung."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?content_type=json")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về content blocks có content_type là json
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], 'Features Block')
    
    def test_filter_by_location(self):
        """Test lọc content blocks theo vị trí."""
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?location=home_")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Nên trả về content blocks có location bắt đầu bằng 'home_'
        self.assertEqual(len(response.data['data']), 2)
        
        # Kiểm tra titles
        block_titles = [block['title'] for block in response.data['data']]
        self.assertIn('Featured Products', block_titles)
        self.assertIn('Features Block', block_titles)
    
    def test_get_by_identifier(self):
        """Test lấy content block theo identifier."""
        # Gọi API với parameter identifier
        response = self.client.get(f"{self.list_url}?identifier=featured_products")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về content block có identifier phù hợp
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['identifier'], 'featured_products')
    
    def test_render_html_content(self):
        """Test endpoint render-content cho content block HTML."""
        # Gọi API
        url = reverse('api:content-blocks-render-content', args=[self.featured_block.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra rendered content
        self.assertIn('rendered_content', response.data['data'])
        self.assertEqual(response.data['data']['rendered_content'], '<p>Check out our featured products!</p>')
    
    def test_parse_json_content(self):
        """Test endpoint parse-json cho content block JSON."""
        # Gọi API
        url = reverse('api:content-blocks-parse-json', args=[self.json_block.id])
        response = self.client.get(url)
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra parsed JSON
        self.assertIn('parsed_json', response.data['data'])
        self.assertIn('features', response.data['data']['parsed_json'])
        self.assertEqual(len(response.data['data']['parsed_json']['features']), 3)
        self.assertIn('Fast Shipping', response.data['data']['parsed_json']['features'])
