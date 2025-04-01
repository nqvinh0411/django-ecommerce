from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Coupon, PromotionCampaign, Voucher, UsageLog


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model with validation logic"""
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_type', 'value', 
                 'min_order_amount', 'max_uses', 'used_count', 
                 'start_date', 'end_date', 'is_active', 'is_valid',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate the coupon data:
        - end_date must be after start_date
        - percentage discounts must be between 0 and 100
        """
        # If both dates are provided, check that end_date is after start_date
        if 'start_date' in data and 'end_date' in data and data['end_date'] and data['start_date']:
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    {'end_date': _('End date must be after start date.')}
                )
        
        # For percentage discounts, check that value is between 0 and 100
        if ('discount_type' in data and data['discount_type'] == 'percent' and 
                'value' in data and float(data['value']) > 100):
            raise serializers.ValidationError(
                {'value': _('Percentage discount cannot exceed 100%.')}
            )
            
        return data


class PromotionCampaignSerializer(serializers.ModelSerializer):
    """Serializer for PromotionCampaign model"""
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PromotionCampaign
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 
                 'is_active', 'is_valid', 'created_at', 'updated_at', 
                 'products', 'categories']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate the campaign data:
        - end_date must be after start_date
        """
        # If both dates are provided, check that end_date is after start_date
        if 'start_date' in data and 'end_date' in data and data['end_date'] and data['start_date']:
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    {'end_date': _('End date must be after start date.')}
                )
                
        return data


class VoucherSerializer(serializers.ModelSerializer):
    """Serializer for Voucher model"""
    
    is_valid = serializers.BooleanField(read_only=True)
    owner_email = serializers.EmailField(source='owner.user.email', read_only=True)
    
    class Meta:
        model = Voucher
        fields = ['id', 'code', 'owner', 'owner_email', 'campaign', 
                 'discount_type', 'value', 'min_order_amount', 
                 'is_used', 'is_valid', 'created_at', 'expired_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """
        Validate the voucher data:
        - expired_at must be in the future
        - percentage discounts must be between 0 and 100
        """
        # Check that expiration date is in the future
        if 'expired_at' in data:
            if data['expired_at'] <= timezone.now():
                raise serializers.ValidationError(
                    {'expired_at': _('Expiration date must be in the future.')}
                )
        
        # For percentage discounts, check that value is between 0 and 100
        if ('discount_type' in data and data['discount_type'] == 'percent' and 
                'value' in data and float(data['value']) > 100):
            raise serializers.ValidationError(
                {'value': _('Percentage discount cannot exceed 100%.')}
            )
            
        return data
    
    def to_representation(self, instance):
        """
        Customize representation based on user permissions:
        - Admins can see all vouchers
        - Customers can only see their own vouchers
        """
        ret = super().to_representation(instance)
        request = self.context.get('request')
        
        # If this is not an admin and not the owner, hide sensitive data
        if request and not request.user.is_staff:
            if hasattr(request.user, 'customer') and request.user.customer != instance.owner:
                ret.pop('code', None)
                ret.pop('discount_type', None)
                ret.pop('value', None)
                ret.pop('min_order_amount', None)
                
        return ret


class UsageLogSerializer(serializers.ModelSerializer):
    """Serializer for UsageLog model"""
    
    customer_email = serializers.EmailField(source='customer.user.email', read_only=True)
    order_number = serializers.IntegerField(source='order.id', read_only=True)
    promo_code = serializers.SerializerMethodField()
    
    class Meta:
        model = UsageLog
        fields = ['id', 'promo_type', 'promo_code', 'customer', 'customer_email',
                 'order', 'order_number', 'discount_amount', 'used_at', 'note']
        read_only_fields = ['id', 'used_at']
    
    def get_promo_code(self, obj):
        if obj.promo_type == 'coupon' and obj.coupon:
            return obj.coupon.code
        elif obj.promo_type == 'voucher' and obj.voucher:
            return obj.voucher.code
        return None


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying a coupon code to an order"""
    
    code = serializers.CharField(max_length=50)
    order_id = serializers.IntegerField()
    
    def validate_code(self, value):
        """Validate that the coupon code exists and is valid"""
        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_valid:
                raise serializers.ValidationError(_('This coupon is no longer valid.'))
            return value
        except Coupon.DoesNotExist:
            # Check if it's a valid voucher code instead
            try:
                voucher = Voucher.objects.get(code=value)
                if not voucher.is_valid:
                    raise serializers.ValidationError(_('This voucher is no longer valid.'))
                return value
            except Voucher.DoesNotExist:
                raise serializers.ValidationError(_('Invalid promotion code.'))
    
    def validate_order_id(self, value):
        """Validate that the order exists and can have a coupon applied"""
        from django.apps import apps
        Order = apps.get_model('orders', 'Order')
        
        try:
            order = Order.objects.get(id=value)
            # Check if the order already has a promotion applied
            if order.promo_usage_logs.exists():
                raise serializers.ValidationError(_('This order already has a promotion applied.'))
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError(_('Invalid order ID.'))


class ApplyVoucherSerializer(ApplyCouponSerializer):
    """Serializer for applying a voucher to an order"""
    
    def validate_code(self, value):
        """Validate that the voucher code exists, belongs to the user, and is valid"""
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'customer'):
            raise serializers.ValidationError(_('Authentication required.'))
            
        try:
            voucher = Voucher.objects.get(code=value, owner=request.user.customer)
            if not voucher.is_valid:
                raise serializers.ValidationError(_('This voucher is no longer valid.'))
            return value
        except Voucher.DoesNotExist:
            raise serializers.ValidationError(_('Invalid voucher code or this voucher does not belong to you.'))
