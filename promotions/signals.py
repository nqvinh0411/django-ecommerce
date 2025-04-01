from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import PromotionCampaign, Voucher, UsageLog


@receiver(post_save, sender=PromotionCampaign)
def create_vouchers_for_campaign(sender, instance, created, **kwargs):
    """
    Signal to automatically create vouchers when a new promotion campaign is created,
    if the campaign is configured to generate vouchers for all customers.
    
    This is just a placeholder - you would typically implement this based on
    specific business rules like generating vouchers for loyal customers.
    """
    # This is an example implementation that would need to be customized
    # based on specific business requirements
    pass


@receiver(post_save, sender=UsageLog)
def update_promotion_usage_statistics(sender, instance, created, **kwargs):
    """
    Signal to update usage statistics when a promotion is used.
    """
    if created:
        # Update coupon used count
        if instance.promo_type == 'coupon' and instance.coupon:
            instance.coupon.used_count += 1
            instance.coupon.save(update_fields=['used_count'])
        
        # Mark voucher as used
        if instance.promo_type == 'voucher' and instance.voucher and not instance.voucher.is_used:
            instance.voucher.is_used = True
            instance.voucher.save(update_fields=['is_used'])


@receiver(post_save, sender='customers.Customer')
def create_welcome_voucher(sender, instance, created, **kwargs):
    """
    Signal to create a welcome voucher for new customers.
    """
    if created:
        # Generate a unique code for the voucher
        import uuid
        code = f"WELCOME-{str(uuid.uuid4()).upper()[:8]}"
        
        # Create the voucher with a 30-day expiration
        Voucher.objects.create(
            code=code,
            owner=instance,
            discount_type='percent',
            value=10,  # 10% discount
            min_order_amount=0,  # No minimum order
            expired_at=timezone.now() + timedelta(days=30)
        )
