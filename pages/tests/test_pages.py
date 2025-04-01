from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from ..models import Page, Banner, MenuItem

User = get_user_model()


class PagesModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create admin user
        cls.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        cls.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        
        # Create a published page
        cls.published_page = Page.objects.create(
            title='About Us',
            slug='about-us',
            content_html='<h1>About Our Store</h1><p>We are an e-commerce store.</p>',
            content_text='About Our Store. We are an e-commerce store.',
            is_published=True,
            published_at=timezone.now(),
            seo_title='About Our E-commerce Store',
            seo_description='Learn more about our e-commerce store and our mission.'
        )
        
        # Create an unpublished page
        cls.unpublished_page = Page.objects.create(
            title='Coming Soon',
            slug='coming-soon',
            content_html='<h1>Coming Soon</h1><p>New products coming soon.</p>',
            content_text='Coming Soon. New products coming soon.',
            is_published=False,
            seo_title='Coming Soon - New Products',
            seo_description='New products coming to our store soon.'
        )
        
        # Create active banner
        cls.active_banner = Banner.objects.create(
            title='Summer Sale',
            image='banners/summer_sale.jpg',
            link_url='/products/?sale=summer',
            position='homepage_top',
            is_active=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Create expired banner
        cls.expired_banner = Banner.objects.create(
            title='Spring Collection',
            image='banners/spring_collection.jpg',
            link_url='/products/?collection=spring',
            position='homepage_middle',
            is_active=True,
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30)
        )
        
        # Create parent menu item
        cls.parent_menu = MenuItem.objects.create(
            label='Products',
            url='/products/',
            order=1,
            is_active=True,
            menu_type='header'
        )
        
        # Create child menu item
        cls.child_menu = MenuItem.objects.create(
            label='Electronics',
            url='/products/electronics/',
            order=1,
            parent=cls.parent_menu,
            is_active=True,
            menu_type='header'
        )

    def test_page_model_str(self):
        """Test the string representation of Page model"""
        self.assertEqual(str(self.published_page), 'About Us')

    def test_banner_model_str(self):
        """Test the string representation of Banner model"""
        self.assertEqual(str(self.active_banner), 'Summer Sale')

    def test_banner_is_expired(self):
        """Test the is_expired property of Banner model"""
        self.assertFalse(self.active_banner.is_expired)
        self.assertTrue(self.expired_banner.is_expired)

    def test_menu_item_str(self):
        """Test the string representation of MenuItem model"""
        self.assertEqual(str(self.parent_menu), 'Products (Header Menu)')

    def test_menu_item_has_children(self):
        """Test the has_children property of MenuItem model"""
        self.assertTrue(self.parent_menu.has_children)
        self.assertFalse(self.child_menu.has_children)


class PagesAPITests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        
        # Create API client
        self.client = APIClient()
        
        # Create a published page
        self.published_page = Page.objects.create(
            title='About Us',
            slug='about-us',
            content_html='<h1>About Our Store</h1><p>We are an e-commerce store.</p>',
            content_text='About Our Store. We are an e-commerce store.',
            is_published=True,
            published_at=timezone.now(),
            seo_title='About Our E-commerce Store',
            seo_description='Learn more about our e-commerce store and our mission.'
        )
        
        # Create an unpublished page
        self.unpublished_page = Page.objects.create(
            title='Coming Soon',
            slug='coming-soon',
            content_html='<h1>Coming Soon</h1><p>New products coming soon.</p>',
            content_text='Coming Soon. New products coming soon.',
            is_published=False,
            seo_title='Coming Soon - New Products',
            seo_description='New products coming to our store soon.'
        )
        
        # Create active banner
        self.active_banner = Banner.objects.create(
            title='Summer Sale',
            image='banners/summer_sale.jpg',
            link_url='/products/?sale=summer',
            position='homepage_top',
            is_active=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Create menu items
        self.header_menu = MenuItem.objects.create(
            label='Products',
            url='/products/',
            order=1,
            is_active=True,
            menu_type='header'
        )
        
        MenuItem.objects.create(
            label='Electronics',
            url='/products/electronics/',
            order=1,
            parent=self.header_menu,
            is_active=True,
            menu_type='header'
        )

    def test_page_list_public(self):
        """Test that public users can only see published pages"""
        url = reverse('page-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only published page

    def test_page_list_admin(self):
        """Test that admin users can see all pages"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('page-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both pages

    def test_page_detail_published(self):
        """Test that public users can see published page details"""
        url = reverse('page-detail', kwargs={'slug': 'about-us'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'About Us')

    def test_page_detail_unpublished(self):
        """Test that public users cannot see unpublished page details"""
        url = reverse('page-detail', kwargs={'slug': 'coming-soon'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_banner_list(self):
        """Test banner list view"""
        url = reverse('banner-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only active banners that haven't expired
        self.assertEqual(len(response.data), 1)

    def test_menu_list(self):
        """Test menu list view for a specific menu type"""
        url = reverse('menu-list', kwargs={'menu_type': 'header'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One parent menu item
        # Check that children are included
        self.assertEqual(len(response.data[0]['children']), 1)
