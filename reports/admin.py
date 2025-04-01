from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SalesReport, ProductReport, CustomerReport, TrafficLog


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'total_orders', 'total_revenue', 
        'total_discount', 'net_revenue', 'updated_at'
    )
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Report Information'), {
            'fields': ('date',)
        }),
        (_('Sales Metrics'), {
            'fields': ('total_orders', 'total_revenue', 'total_discount', 'net_revenue')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductReport)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 'sold_quantity', 'total_revenue', 
        'average_rating', 'last_sold_at', 'updated_at'
    )
    list_filter = ('last_sold_at', 'average_rating')
    search_fields = ('product__name', 'product__description')
    readonly_fields = ('created_at', 'updated_at')
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = _('Product Name')
    product_name.admin_order_field = 'product__name'
    
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product',)
        }),
        (_('Performance Metrics'), {
            'fields': ('sold_quantity', 'total_revenue', 'average_rating', 'last_sold_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerReport)
class CustomerReportAdmin(admin.ModelAdmin):
    list_display = (
        'customer_email', 'total_orders', 'total_spent', 
        'average_order_value', 'last_order_at', 'updated_at'
    )
    list_filter = ('last_order_at', 'total_orders')
    search_fields = ('customer__user__email', 'customer__user__first_name', 'customer__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def customer_email(self, obj):
        return obj.customer.user.email
    customer_email.short_description = _('Customer Email')
    customer_email.admin_order_field = 'customer__user__email'
    
    fieldsets = (
        (_('Customer Information'), {
            'fields': ('customer',)
        }),
        (_('Purchase Metrics'), {
            'fields': ('total_orders', 'total_spent', 'average_order_value', 'last_order_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TrafficLog)
class TrafficLogAdmin(admin.ModelAdmin):
    list_display = (
        'endpoint', 'method', 'ip_address',
        'duration_ms', 'timestamp'
    )
    list_filter = ('method', 'timestamp')
    search_fields = ('endpoint', 'ip_address')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        (_('Request Information'), {
            'fields': ('endpoint', 'method', 'ip_address')
        }),
        (_('Performance'), {
            'fields': ('duration_ms',)
        }),
        (_('Additional Information'), {
            'fields': ('user_agent', 'timestamp')
        }),
    )
