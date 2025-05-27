"""
Unit tests for Settings ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Settings,
bao gồm StoreSettingViewSet, CurrencyViewSet, LanguageSettingViewSet và EmailTemplateViewSet.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import StoreSetting, Currency, LanguageSetting, EmailTemplate
from ..serializers import (
    StoreSettingSerializer, CurrencySerializer, 
    LanguageSettingSerializer, EmailTemplateSerializer
)

from core.tests.test_viewsets import StandardizedViewSetTestCase
from core.tests.test_utils import BaseAPITestCase, TestDataGenerator

User = get_user_model()


class StoreSettingViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for StoreSettingViewSet.
    """
    
    model_class = StoreSetting
    serializer_class = StoreSettingSerializer
    base_url_name = 'store-settings'
    
    def setUp(self):
        """Set up specific test data for StoreSetting."""
        super().setUp()
        
        # Tạo dữ liệu test cho Currency
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            exchange_rate_to_base=1.0,
            is_default=True
        )
        
        # Tạo dữ liệu test cho LanguageSetting
        self.language = LanguageSetting.objects.create(
            code='en',
            name='English',
            is_default=True
        )
        
        # Thiết lập dữ liệu hợp lệ cho việc tạo và cập nhật
        self.valid_create_data = {
            'store_name': 'Test Store',
            'support_email': 'support@teststore.com',
            'contact_phone': '+1234567890',
            'default_currency_id': self.currency.id,
            'default_language_id': self.language.id,
            'maintenance_mode': False,
            'allow_guest_checkout': True,
            'enable_tax': True,
            'enable_inventory_tracking': True
        }
        
        self.valid_update_data = {
            'store_name': 'Updated Test Store',
            'support_email': 'updated-support@teststore.com',
            'maintenance_mode': True,
            'allow_guest_checkout': False
        }
        
        # Tạo StoreSetting cho test
        self.store_setting = StoreSetting.objects.create(
            store_name='Existing Store',
            support_email='existing@store.com',
            contact_phone='+9876543210',
            default_currency=self.currency,
            default_language=self.language,
            maintenance_mode=False,
            allow_guest_checkout=True,
            enable_tax=True,
            enable_inventory_tracking=True
        )
    
    def test_toggle_maintenance_endpoint(self):
        """Test endpoint toggle-maintenance."""
        # Chuẩn bị dữ liệu
        toggle_data = {
            'maintenance_mode': True
        }
        
        # Gọi API
        url = reverse('api:store-settings-toggle-maintenance')
        response = self.client.post(url, toggle_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra trạng thái bảo trì đã được cập nhật
        self.store_setting.refresh_from_db()
        self.assertEqual(self.store_setting.maintenance_mode, True)
    
    def test_update_store_contact_info(self):
        """Test cập nhật thông tin liên hệ của cửa hàng."""
        # Chuẩn bị dữ liệu
        contact_data = {
            'support_email': 'new-support@teststore.com',
            'contact_phone': '+1122334455'
        }
        
        # Gọi API
        url = self.get_detail_url(self.store_setting.id)
        response = self.client.patch(url, contact_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra thông tin liên hệ đã được cập nhật
        self.store_setting.refresh_from_db()
        self.assertEqual(self.store_setting.support_email, 'new-support@teststore.com')
        self.assertEqual(self.store_setting.contact_phone, '+1122334455')
    
    def test_get_active_settings(self):
        """Test lấy cài đặt cửa hàng đang hoạt động."""
        # Tạo cài đặt khác
        inactive_setting = StoreSetting.objects.create(
            store_name='Inactive Store',
            support_email='inactive@store.com',
            default_currency=self.currency,
            default_language=self.language,
            is_active=False
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về cài đặt đang hoạt động
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['store_name'], 'Existing Store')


class CurrencyViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for CurrencyViewSet.
    """
    
    model_class = Currency
    serializer_class = CurrencySerializer
    base_url_name = 'currencies'
    
    valid_create_data = {
        'code': 'EUR',
        'name': 'Euro',
        'symbol': '€',
        'exchange_rate_to_base': 0.85,
        'is_default': False
    }
    
    valid_update_data = {
        'name': 'Updated Euro',
        'exchange_rate_to_base': 0.88
    }
    
    def setUp(self):
        """Set up specific test data for Currency."""
        super().setUp()
        
        # Tạo Currency mặc định
        self.default_currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            exchange_rate_to_base=1.0,
            is_default=True
        )
    
    def test_set_default_currency(self):
        """Test thiết lập tiền tệ mặc định."""
        # Tạo tiền tệ mới
        new_currency = Currency.objects.create(
            code='GBP',
            name='British Pound',
            symbol='£',
            exchange_rate_to_base=0.75,
            is_default=False
        )
        
        # Chuẩn bị dữ liệu
        default_data = {
            'is_default': True
        }
        
        # Gọi API
        url = self.get_detail_url(new_currency.id)
        response = self.client.patch(url, default_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra tiền tệ mới đã được đặt làm mặc định
        new_currency.refresh_from_db()
        self.default_currency.refresh_from_db()
        
        self.assertEqual(new_currency.is_default, True)
        self.assertEqual(self.default_currency.is_default, False)  # Tiền tệ trước không còn là mặc định
    
    def test_search_currency_by_code(self):
        """Test tìm kiếm tiền tệ theo mã."""
        # Tạo nhiều tiền tệ
        Currency.objects.create(
            code='GBP',
            name='British Pound',
            symbol='£',
            exchange_rate_to_base=0.75
        )
        
        Currency.objects.create(
            code='JPY',
            name='Japanese Yen',
            symbol='¥',
            exchange_rate_to_base=110.0
        )
        
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=GB")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về tiền tệ GBP
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['code'], 'GBP')


class LanguageSettingViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for LanguageSettingViewSet.
    """
    
    model_class = LanguageSetting
    serializer_class = LanguageSettingSerializer
    base_url_name = 'languages'
    
    valid_create_data = {
        'code': 'fr',
        'name': 'French',
        'is_default': False,
        'is_active': True
    }
    
    valid_update_data = {
        'name': 'Updated French',
        'is_active': False
    }
    
    def setUp(self):
        """Set up specific test data for LanguageSetting."""
        super().setUp()
        
        # Tạo ngôn ngữ mặc định
        self.default_language = LanguageSetting.objects.create(
            code='en',
            name='English',
            is_default=True,
            is_active=True
        )
    
    def test_set_default_language(self):
        """Test thiết lập ngôn ngữ mặc định."""
        # Tạo ngôn ngữ mới
        new_language = LanguageSetting.objects.create(
            code='es',
            name='Spanish',
            is_default=False,
            is_active=True
        )
        
        # Chuẩn bị dữ liệu
        default_data = {
            'is_default': True
        }
        
        # Gọi API
        url = self.get_detail_url(new_language.id)
        response = self.client.patch(url, default_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra ngôn ngữ mới đã được đặt làm mặc định
        new_language.refresh_from_db()
        self.default_language.refresh_from_db()
        
        self.assertEqual(new_language.is_default, True)
        self.assertEqual(self.default_language.is_default, False)  # Ngôn ngữ trước không còn là mặc định
    
    def test_filter_by_active_status(self):
        """Test lọc ngôn ngữ theo trạng thái hoạt động."""
        # Tạo ngôn ngữ không hoạt động
        inactive_language = LanguageSetting.objects.create(
            code='de',
            name='German',
            is_default=False,
            is_active=False
        )
        
        # Gọi API với filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về ngôn ngữ đang hoạt động
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['code'], 'en')


class EmailTemplateViewSetTests(StandardizedViewSetTestCase):
    """
    Test cases for EmailTemplateViewSet.
    """
    
    model_class = EmailTemplate
    serializer_class = EmailTemplateSerializer
    base_url_name = 'email-templates'
    
    valid_create_data = {
        'template_key': 'welcome_email',
        'subject': 'Welcome to our store',
        'body_html': '<p>Welcome to our store!</p>',
        'body_text': 'Welcome to our store!',
        'is_active': True
    }
    
    valid_update_data = {
        'subject': 'Updated Welcome Email',
        'body_html': '<p>Updated welcome message!</p>',
        'body_text': 'Updated welcome message!'
    }
    
    def setUp(self):
        """Set up specific test data for EmailTemplate."""
        super().setUp()
        
        # Tạo email template
        self.template = EmailTemplate.objects.create(
            template_key='order_confirmation',
            subject='Order Confirmation',
            body_html='<p>Your order has been confirmed.</p>',
            body_text='Your order has been confirmed.',
            is_active=True
        )
    
    def test_search_template_by_key(self):
        """Test tìm kiếm template theo key."""
        # Tạo nhiều templates
        EmailTemplate.objects.create(
            template_key='password_reset',
            subject='Password Reset',
            body_html='<p>Reset your password.</p>',
            body_text='Reset your password.',
            is_active=True
        )
        
        # Gọi API với tham số tìm kiếm
        response = self.client.get(f"{self.list_url}?search=password")
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Chỉ nên trả về template password_reset
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['template_key'], 'password_reset')
    
    def test_preview_template_endpoint(self):
        """Test endpoint preview-template."""
        # Chuẩn bị dữ liệu
        preview_data = {
            'template_key': 'order_confirmation',
            'context': {
                'order_number': '12345',
                'customer_name': 'John Doe'
            }
        }
        
        # Gọi API
        url = reverse('api:email-templates-preview')
        response = self.client.post(url, preview_data, format='json')
        
        # Kiểm tra response
        self.assert_status(response, status.HTTP_200_OK)
        
        # Kiểm tra response có chứa nội dung preview
        self.assertIn('preview', response.data['data'])
        self.assertIn('subject', response.data['data'])
        self.assertIn('body_html', response.data['data'])
        self.assertIn('body_text', response.data['data'])
