from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Coupon(models.Model):
    """Model for store-wide discount coupons"""
    
    DISCOUNT_TYPE_CHOICES = (
        ('percent', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    )
    
    code = models.CharField(_('Coupon Code'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True)
    discount_type = models.CharField(
        _('Discount Type'), 
        max_length=10, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default='percent'
    )
    value = models.DecimalField(
        _('Discount Value'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    min_order_amount = models.DecimalField(
        _('Minimum Order Amount'), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_uses = models.PositiveIntegerField(_('Maximum Uses'), default=0, help_text=_('0 for unlimited uses'))
    used_count = models.PositiveIntegerField(_('Used Count'), default=0)
    start_date = models.DateTimeField(_('Valid From'), default=timezone.now)
    end_date = models.DateTimeField(_('Valid Until'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} ({self.value})"
    
    @property
    def is_valid(self):
        """Check if the coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True
    
    def calculate_discount(self, order_amount):
        """Calculate the discount amount for an order"""
        if not self.is_valid or order_amount < self.min_order_amount:
            return 0
        
        if self.discount_type == 'percent':
            # Ensure percentage is between 0 and 100
            percent = min(max(float(self.value), 0), 100)
            return (percent / 100) * order_amount
        else:  # fixed amount
            # Ensure fixed discount doesn't exceed order amount
            return min(float(self.value), order_amount)


class PromotionCampaign(models.Model):
    """Model for promotion campaigns"""
    
    name = models.CharField(_('Campaign Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    start_date = models.DateTimeField(_('Start Date'), default=timezone.now)
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    # Optional relations to products or categories if campaign applies to specific items
    products = models.ManyToManyField('products.Product', blank=True, related_name='campaigns')
    categories = models.ManyToManyField('catalog.Category', blank=True, related_name='campaigns')
    
    class Meta:
        verbose_name = _('Promotion Campaign')
        verbose_name_plural = _('Promotion Campaigns')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    @property
    def is_valid(self):
        """Check if the campaign is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Voucher(models.Model):
    """Model for customer-specific vouchers"""
    
    code = models.CharField(_('Voucher Code'), max_length=50, unique=True)
    owner = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='vouchers')
    campaign = models.ForeignKey(PromotionCampaign, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='vouchers')
    discount_type = models.CharField(
        _('Discount Type'), 
        max_length=10, 
        choices=Coupon.DISCOUNT_TYPE_CHOICES, 
        default='percent'
    )
    value = models.DecimalField(
        _('Discount Value'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    min_order_amount = models.DecimalField(
        _('Minimum Order Amount'), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_used = models.BooleanField(_('Used'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    expired_at = models.DateTimeField(_('Expires At'))
    
    class Meta:
        verbose_name = _('Voucher')
        verbose_name_plural = _('Vouchers')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.owner}"
    
    @property
    def is_valid(self):
        """Check if the voucher is currently valid"""
        now = timezone.now()
        if self.is_used:
            return False
        if now > self.expired_at:
            return False
        return True
    
    def calculate_discount(self, order_amount):
        """Calculate the discount amount for an order"""
        if not self.is_valid or order_amount < self.min_order_amount:
            return 0
        
        if self.discount_type == 'percent':
            # Ensure percentage is between 0 and 100
            percent = min(max(float(self.value), 0), 100)
            return (percent / 100) * order_amount
        else:  # fixed amount
            # Ensure fixed discount doesn't exceed order amount
            return min(float(self.value), order_amount)


class UsageLog(models.Model):
    """Model for tracking coupon and voucher usage"""
    
    PROMO_TYPE_CHOICES = (
        ('coupon', _('Coupon')),
        ('voucher', _('Voucher')),
    )
    
    promo_type = models.CharField(_('Promotion Type'), max_length=10, choices=PROMO_TYPE_CHOICES)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='usage_logs')
    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True, related_name='usage_logs')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='promo_usage_logs')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='promo_usage_logs')
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(_('Used At'), auto_now_add=True)
    note = models.TextField(_('Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Usage Log')
        verbose_name_plural = _('Usage Logs')
        ordering = ['-used_at']
    
    def __str__(self):
        promo_code = self.coupon.code if self.coupon else (self.voucher.code if self.voucher else 'Unknown')
        return f"{self.get_promo_type_display()}: {promo_code} - Order #{self.order.id}"
    
    def save(self, *args, **kwargs):
        # Update the used count for coupons
        if self.promo_type == 'coupon' and self.coupon:
            self.coupon.used_count += 1
            self.coupon.save()
        
        # Mark voucher as used
        if self.promo_type == 'voucher' and self.voucher and not self.voucher.is_used:
            self.voucher.is_used = True
            self.voucher.save()
            
        super().save(*args, **kwargs)
