from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from promotions.models import Coupon, PromotionCampaign, Voucher, UsageLog


class CouponModelTest(TestCase):
    """Test cases for the Coupon model"""
    
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="TEST10",
            description="Test coupon",
            discount_type="percent",
            value=10,
            min_order_amount=50,
            max_uses=100,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_coupon_is_valid(self):
        """Test the is_valid property for a valid coupon"""
        self.assertTrue(self.coupon.is_valid)
    
    def test_coupon_calculate_discount_percent(self):
        """Test discount calculation for percentage discount"""
        self.assertEqual(self.coupon.calculate_discount(100), 10)
        # Below minimum order amount
        self.assertEqual(self.coupon.calculate_discount(40), 0)
    
    def test_coupon_str_representation(self):
        """Test string representation of a coupon"""
        self.assertEqual(str(self.coupon), "TEST10 - Percentage (10)")


class VoucherModelTest(TestCase):
    """Test cases for the Voucher model"""
    
    def setUp(self):
        # This would require creating a Customer object first,
        # which depends on your Customer model implementation
        pass
    
    def test_voucher_is_valid(self):
        """Test the is_valid property for vouchers"""
        # Implementation depends on having a customer model
        pass


class PromotionCampaignModelTest(TestCase):
    """Test cases for the PromotionCampaign model"""
    
    def setUp(self):
        self.campaign = PromotionCampaign.objects.create(
            name="Summer Sale",
            description="Summer discount campaign",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
    
    def test_campaign_is_valid(self):
        """Test the is_valid property for a campaign"""
        self.assertTrue(self.campaign.is_valid)
    
    def test_campaign_str_representation(self):
        """Test string representation of a campaign"""
        self.assertEqual(str(self.campaign), "Summer Sale")
