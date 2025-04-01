from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import StoreSetting, Currency, LanguageSetting, EmailTemplate

User = get_user_model()


class SettingsModelTests(TestCase):
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
        
        # Create default currency
        cls.default_currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            exchange_rate_to_base=1.0,
            is_default=True
        )
        
        # Create second currency
        cls.second_currency = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€',
            exchange_rate_to_base=0.85,
            is_default=False
        )
        
        # Create default language
        cls.default_language = LanguageSetting.objects.create(
            code='en',
            name='English',
            is_default=True
        )
        
        # Create store settings
        cls.store_settings = StoreSetting.objects.create(
            store_name='Test Store',
            support_email='support@teststore.com',
            phone_number='123-456-7890',
            address='123 Test St, Test City',
            default_currency=cls.default_currency,
            default_language=cls.default_language
        )
        
        # Create email template
        cls.email_template = EmailTemplate.objects.create(
            template_key='welcome_email',
            subject='Welcome to our store',
            body_html='<p>Welcome, {{name}}!</p>',
            body_text='Welcome, {{name}}!'
        )

    def test_store_setting_str(self):
        """Test the string representation of the StoreSetting model"""
        self.assertEqual(str(self.store_settings), 'Test Store')

    def test_currency_str(self):
        """Test the string representation of the Currency model"""
        self.assertEqual(str(self.default_currency), 'USD - US Dollar')

    def test_language_setting_str(self):
        """Test the string representation of the LanguageSetting model"""
        self.assertEqual(str(self.default_language), 'English (en)')

    def test_email_template_str(self):
        """Test the string representation of the EmailTemplate model"""
        self.assertEqual(str(self.email_template), 'welcome_email')

    def test_only_one_default_currency(self):
        """Test that only one currency can be default"""
        # Change the second currency to default
        self.second_currency.is_default = True
        self.second_currency.save()
        
        # Refresh the default currency from the database
        self.default_currency.refresh_from_db()
        
        # The first currency should no longer be default
        self.assertFalse(self.default_currency.is_default)
        self.assertTrue(self.second_currency.is_default)

    def test_only_one_default_language(self):
        """Test that only one language can be default"""
        # Create a second language and set it as default
        second_language = LanguageSetting.objects.create(
            code='fr',
            name='French',
            is_default=True
        )
        
        # Refresh the default language from the database
        self.default_language.refresh_from_db()
        
        # The first language should no longer be default
        self.assertFalse(self.default_language.is_default)
        self.assertTrue(second_language.is_default)

    def test_only_one_store_setting(self):
        """Test that only one store setting can exist"""
        # Trying to create a second store setting should raise an error
        with self.assertRaises(Exception):
            StoreSetting.objects.create(
                store_name='Another Store',
                support_email='support@anotherstore.com'
            )

    def test_get_settings_creates_if_not_exists(self):
        """Test that get_settings creates a new setting if none exists"""
        # Delete all settings
        StoreSetting.objects.all().delete()
        
        # Call get_settings
        settings = StoreSetting.get_settings()
        
        # Check that a new setting was created
        self.assertEqual(StoreSetting.objects.count(), 1)
        self.assertEqual(settings, StoreSetting.objects.first())


class SettingsAPITests(TestCase):
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
        
        # Create default currency and language
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_default=True
        )
        
        self.language = LanguageSetting.objects.create(
            code='en',
            name='English',
            is_default=True
        )
        
        # Create store settings
        self.store_settings = StoreSetting.objects.create(
            store_name='Test Store',
            support_email='support@teststore.com',
            default_currency=self.currency,
            default_language=self.language
        )
        
        # Create email template
        self.email_template = EmailTemplate.objects.create(
            template_key='test_template',
            subject='Test Subject',
            body_html='<p>Test HTML</p>',
            body_text='Test Text'
        )

    def test_store_setting_endpoint_admin_access(self):
        """Test that admin users can access store settings"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('store-setting')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['store_name'], 'Test Store')

    def test_store_setting_endpoint_non_admin_denied(self):
        """Test that non-admin users cannot access store settings"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('store-setting')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_currency_list_endpoint_admin_access(self):
        """Test that admin users can access currency list"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('currency-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_language_list_endpoint_admin_access(self):
        """Test that admin users can access language list"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('language-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_email_template_create_and_retrieve(self):
        """Test creating and retrieving email templates"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a new template
        url = reverse('email-template-list')
        data = {
            'template_key': 'new_template',
            'subject': 'New Subject',
            'body_html': '<p>New HTML</p>',
            'body_text': 'New Text'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Retrieve the template
        template_id = response.data['id']
        url = reverse('email-template-detail', kwargs={'pk': template_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['template_key'], 'new_template')
