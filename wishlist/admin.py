from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ('added_at',)
    autocomplete_fields = ('product',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_email', 'items_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__user__email', 'items__product__name')
    inlines = (WishlistItemInline,)
    readonly_fields = ('created_at',)
    
    def customer_email(self, obj):
        return obj.customer.user.email
    customer_email.short_description = _('Customer Email')
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = _('Number of Items')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'customer_email', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('wishlist__customer__user__email', 'product__name')
    readonly_fields = ('added_at',)
    autocomplete_fields = ('wishlist', 'product')
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = _('Product')
    
    def customer_email(self, obj):
        return obj.wishlist.customer.user.email
    customer_email.short_description = _('Customer Email')
