"""
Unit tests for Promotions ViewSets.

Module này chứa các test cases cho tất cả ViewSets trong module Promotions,
bao gồm CouponViewSet, PromotionCampaignViewSet, VoucherViewSet và UsageLogViewSet.
"""
import json
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Coupon, PromotionCampaign, Voucher, UsageLog
from ..serializers import (
    CouponSerializer, PromotionCampaignSerializer, 
    VoucherSerializer, UsageLogSerializer
)

User = get_user_model()


class BasePromotionsTestCase(TestCase):
    """
    Base test case for Promotions tests with common setup.
    """
    
    def setUp(self):
        """Set up common test data."""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpassword123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword123'
        )
        
        # Create API client
        self.client = APIClient()
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create test data for promotions."""
        # Create coupons
        self.coupon_percentage = Coupon.objects.create(
            code='TEST10',
            discount_type='percentage',
            discount_value=10,
            min_purchase_amount=100,
            max_discount_amount=50,
            valid_from=timezone.now() - timedelta(days=10),
            valid_to=timezone.now() + timedelta(days=10),
            is_active=True,
            usage_limit=100,
            usage_count=0
        )
        
        self.coupon_fixed = Coupon.objects.create(
            code='FIXED20',
            discount_type='fixed',
            discount_value=20,
            min_purchase_amount=50,
            valid_from=timezone.now() - timedelta(days=5),
            valid_to=timezone.now() + timedelta(days=5),
            is_active=True,
            usage_limit=50,
            usage_count=0
        )
        
        self.inactive_coupon = Coupon.objects.create(
            code='INACTIVE',
            discount_type='percentage',
            discount_value=15,
            min_purchase_amount=0,
            valid_from=timezone.now() - timedelta(days=30),
            valid_to=timezone.now() - timedelta(days=1),
            is_active=False,
            usage_limit=10,
            usage_count=0
        )
        
        # Create promotion campaigns
        self.promotion_campaign = PromotionCampaign.objects.create(
            name='Summer Sale',
            description='Summer sale with great discounts',
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        self.promotion_campaign_inactive = PromotionCampaign.objects.create(
            name='Winter Sale',
            description='Winter clearance',
            start_date=timezone.now() + timedelta(days=60),
            end_date=timezone.now() + timedelta(days=90),
            is_active=False
        )
        
        # Create vouchers
        self.voucher = Voucher.objects.create(
            code='VOUCHER50',
            discount_type='percentage',
            discount_value=50,
            min_purchase_amount=200,
            max_discount_amount=100,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=30),
            is_active=True,
            usage_limit=1,
            usage_count=0,
            is_single_use=True
        )


class PromotionCampaignViewSetTests(BasePromotionsTestCase):
    """
    Test cases for PromotionCampaignViewSet.
    """
    
    def setUp(self):
        """Set up specific test data for PromotionCampaign."""
        super().setUp()
        self.list_url = reverse('api:promotion-campaigns-list')
    
    def get_detail_url(self, pk):
        """Helper to get detail URL for a promotion campaign."""
        return reverse('api:promotion-campaigns-detail', args=[pk])
    
    def test_list_promotion_campaigns(self):
        """Test retrieving a list of promotion campaigns."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request
        response = self.client.get(self.list_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response data contains both active and inactive campaigns
        self.assertEqual(len(response.data['data']), 2)
        
        # Verify response format
        self.assertIn('status', response.data)
        self.assertIn('status_code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
    
    def test_retrieve_promotion_campaign(self):
        """Test retrieving a single promotion campaign."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request
        url = self.get_detail_url(self.promotion_campaign.id)
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify campaign details
        self.assertEqual(response.data['data']['id'], self.promotion_campaign.id)
        self.assertEqual(response.data['data']['name'], 'Summer Sale')
        self.assertEqual(response.data['data']['is_active'], True)
    
    def test_create_promotion_campaign(self):
        """Test creating a new promotion campaign."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare data
        new_campaign_data = {
            'name': 'Black Friday Sale',
            'description': 'Biggest sale of the year',
            'start_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=32)).isoformat(),
            'is_active': True
        }
        
        # Make request
        response = self.client.post(
            self.list_url,
            data=json.dumps(new_campaign_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify new campaign was created
        self.assertEqual(PromotionCampaign.objects.count(), 3)
        
        # Verify campaign details
        new_campaign = PromotionCampaign.objects.get(name='Black Friday Sale')
        self.assertEqual(new_campaign.description, 'Biggest sale of the year')
        self.assertEqual(new_campaign.is_active, True)
    
    def test_update_promotion_campaign(self):
        """Test updating an existing promotion campaign."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare data
        updated_data = {
            'name': 'Updated Summer Sale',
            'description': 'Updated description',
            'is_active': False
        }
        
        # Make request
        url = self.get_detail_url(self.promotion_campaign.id)
        response = self.client.patch(
            url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify campaign was updated
        updated_campaign = PromotionCampaign.objects.get(id=self.promotion_campaign.id)
        self.assertEqual(updated_campaign.name, 'Updated Summer Sale')
        self.assertEqual(updated_campaign.description, 'Updated description')
        self.assertEqual(updated_campaign.is_active, False)
    
    def test_delete_promotion_campaign(self):
        """Test deleting a promotion campaign."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request
        url = self.get_detail_url(self.promotion_campaign.id)
        response = self.client.delete(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify campaign was deleted
        self.assertEqual(PromotionCampaign.objects.filter(id=self.promotion_campaign.id).count(), 0)
    
    def test_permission_staff_can_view(self):
        """Test that staff users can view promotion campaigns."""
        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)
        
        # Make request
        response = self.client.get(self.list_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_permission_regular_user_denied(self):
        """Test that regular users cannot access promotion campaigns."""
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make request
        response = self.client.get(self.list_url)
        
        # Check response - should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_filter_active_campaigns(self):
        """Test filtering promotion campaigns by active status."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request with filter
        response = self.client.get(f"{self.list_url}?is_active=true")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return active campaigns
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Summer Sale')
    
    def test_validation_error_end_date_before_start_date(self):
        """Test validation error when end date is before start date."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare invalid data
        invalid_data = {
            'name': 'Invalid Campaign',
            'description': 'This campaign has invalid dates',
            'start_date': (timezone.now() + timedelta(days=10)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=5)).isoformat(),
            'is_active': True
        }
        
        # Make request
        response = self.client.post(
            self.list_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Check response - should be bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify campaign was not created
        self.assertEqual(PromotionCampaign.objects.filter(name='Invalid Campaign').count(), 0)


class CouponViewSetTests(BasePromotionsTestCase):
    """
    Test cases for CouponViewSet.
    """
    
    def setUp(self):
        """Set up specific test data for Coupon."""
        super().setUp()
        self.list_url = reverse('api:coupons-list')
    
    def get_detail_url(self, pk):
        """Helper to get detail URL for a coupon."""
        return reverse('api:coupons-detail', args=[pk])
    
    def test_list_coupons(self):
        """Test retrieving a list of coupons."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request
        response = self.client.get(self.list_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all coupons are returned
        self.assertEqual(len(response.data['data']), 3)
    
    def test_retrieve_coupon(self):
        """Test retrieving a single coupon."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request
        url = self.get_detail_url(self.coupon_percentage.id)
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify coupon details
        self.assertEqual(response.data['data']['code'], 'TEST10')
        self.assertEqual(response.data['data']['discount_type'], 'percentage')
        self.assertEqual(response.data['data']['discount_value'], 10)
    
    def test_apply_coupon_valid(self):
        """Test applying a valid coupon."""
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare data
        apply_data = {
            'code': 'TEST10',
            'order_total': 200
        }
        
        # Make request
        url = reverse('api:coupons-apply-coupon')
        response = self.client.post(
            url,
            data=json.dumps(apply_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify discount calculated correctly (10% of 200 = 20)
        self.assertEqual(response.data['data']['discount_amount'], 20)
        self.assertEqual(response.data['data']['is_valid'], True)
    
    def test_apply_coupon_invalid_code(self):
        """Test applying a coupon with invalid code."""
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare data
        apply_data = {
            'code': 'NONEXISTENT',
            'order_total': 200
        }
        
        # Make request
        url = reverse('api:coupons-apply-coupon')
        response = self.client.post(
            url,
            data=json.dumps(apply_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Mã giảm giá không tồn tại', str(response.data))
    
    def test_apply_coupon_below_min_purchase(self):
        """Test applying a coupon below minimum purchase amount."""
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare data (min purchase is 100, using 50)
        apply_data = {
            'code': 'TEST10',
            'order_total': 50
        }
        
        # Make request
        url = reverse('api:coupons-apply-coupon')
        response = self.client.post(
            url,
            data=json.dumps(apply_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('đơn hàng tối thiểu', str(response.data))


# Similar test classes would be created for VoucherViewSet and UsageLogViewSet
