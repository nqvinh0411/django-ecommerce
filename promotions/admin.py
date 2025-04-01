from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Coupon, PromotionCampaign, Voucher, UsageLog


class UsageLogInline(admin.TabularInline):
    model = UsageLog
    fields = ('customer', 'order', 'discount_amount', 'used_at')
    readonly_fields = ('customer', 'order', 'discount_amount', 'used_at')
    extra = 0
    can_delete = False
    max_num = 10
    verbose_name = _("Usage Record")
    verbose_name_plural = _("Usage Records")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'used_count', 'max_uses', 
                   'start_date', 'end_date', 'is_active', 'is_valid')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at', 'is_valid')
    fieldsets = (
        (None, {
            'fields': ('code', 'description')
        }),
        (_('Discount Information'), {
            'fields': ('discount_type', 'value', 'min_order_amount')
        }),
        (_('Validity'), {
            'fields': ('start_date', 'end_date', 'max_uses', 'used_count', 'is_active')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_valid'),
            'classes': ('collapse',)
        }),
    )
    inlines = [UsageLogInline]
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = _('Is Valid')


@admin.register(PromotionCampaign)
class PromotionCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'is_valid')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'is_valid')
    filter_horizontal = ('products', 'categories')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Validity'), {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        (_('Product Association'), {
            'fields': ('products', 'categories')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_valid'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = _('Is Valid')


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'owner', 'discount_type', 'value', 'is_used', 'created_at', 'expired_at')
    list_filter = ('discount_type', 'is_used', 'created_at', 'expired_at')
    search_fields = ('code', 'owner__user__username', 'owner__user__email')
    readonly_fields = ('created_at', 'is_valid')
    fieldsets = (
        (None, {
            'fields': ('code', 'owner', 'campaign')
        }),
        (_('Discount Information'), {
            'fields': ('discount_type', 'value', 'min_order_amount')
        }),
        (_('Status'), {
            'fields': ('is_used', 'expired_at', 'is_valid')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    inlines = [UsageLogInline]
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = _('Is Valid')


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ('get_promo_code', 'promo_type', 'customer', 'order', 'discount_amount', 'used_at')
    list_filter = ('promo_type', 'used_at')
    search_fields = ('coupon__code', 'voucher__code', 'customer__user__email', 'order__id')
    readonly_fields = ('used_at',)
    
    def get_promo_code(self, obj):
        if obj.promo_type == 'coupon' and obj.coupon:
            return obj.coupon.code
        elif obj.promo_type == 'voucher' and obj.voucher:
            return obj.voucher.code
        return "-"
    get_promo_code.short_description = _('Promo Code')
