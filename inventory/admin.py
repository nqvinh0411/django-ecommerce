from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Warehouse, StockItem, StockMovement, InventoryAuditLog
from django.db.models import models


class StockItemInline(admin.TabularInline):
    model = StockItem
    extra = 0
    fields = ('product', 'quantity', 'low_stock_threshold', 'is_tracked')
    raw_id_fields = ('product',)
    

class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_default', 'is_active', 'created_at')
    list_filter = ('is_default', 'is_active')
    search_fields = ('name', 'location', 'description')
    list_editable = ('is_active',)
    inlines = [StockItemInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'location')
        }),
        (_('Details'), {
            'fields': ('description', 'is_default', 'is_active')
        }),
    )


class LowStockFilter(admin.SimpleListFilter):
    title = _('Stock Status')
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('low', _('Low Stock')),
            ('out', _('Out of Stock')),
            ('in_stock', _('In Stock')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(
                quantity__lte=models.F('low_stock_threshold'), 
                quantity__gt=0,
                is_tracked=True
            )
        if self.value() == 'out':
            return queryset.filter(quantity=0, is_tracked=True)
        if self.value() == 'in_stock':
            return queryset.filter(
                quantity__gt=models.F('low_stock_threshold'),
                is_tracked=True
            )
        return queryset


class StockItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'warehouse_name', 'quantity', 'low_stock_threshold', 
                   'is_tracked', 'stock_status', 'last_updated')
    list_filter = ('warehouse', 'is_tracked', LowStockFilter)
    search_fields = ('product__name', 'warehouse__name')
    list_editable = ('quantity', 'low_stock_threshold', 'is_tracked')
    raw_id_fields = ('product',)
    
    def product_name(self, obj):
        return obj.product.name if hasattr(obj.product, 'name') else str(obj.product)
    product_name.short_description = _('Product')
    product_name.admin_order_field = 'product__name'
    
    def warehouse_name(self, obj):
        return obj.warehouse.name
    warehouse_name.short_description = _('Warehouse')
    warehouse_name.admin_order_field = 'warehouse__name'
    
    def stock_status(self, obj):
        if not obj.is_tracked:
            return _('Not Tracked')
        if obj.quantity <= 0:
            return _('Out of Stock')
        if obj.quantity <= obj.low_stock_threshold:
            return _('Low Stock')
        return _('In Stock')
    stock_status.short_description = _('Status')


class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'product_name', 'quantity', 'reason', 
                   'related_order_display', 'created_by', 'created_at')
    list_filter = ('movement_type', 'stock_item__warehouse', 'created_at')
    search_fields = ('stock_item__product__name', 'reason')
    raw_id_fields = ('stock_item', 'related_order', 'created_by')
    
    def product_name(self, obj):
        return obj.stock_item.product.name if hasattr(obj.stock_item.product, 'name') else str(obj.stock_item.product)
    product_name.short_description = _('Product')
    
    def related_order_display(self, obj):
        if obj.related_order:
            return f"#{obj.related_order.id}" if hasattr(obj.related_order, 'id') else str(obj.related_order)
        return "-"
    related_order_display.short_description = _('Order')


class InventoryAuditLogAdmin(admin.ModelAdmin):
    list_display = ('stock_item_name', 'change_type', 'old_quantity', 'new_quantity', 
                   'changed_by', 'created_at')
    list_filter = ('change_type', 'stock_item__warehouse', 'created_at')
    search_fields = ('stock_item__product__name', 'note')
    readonly_fields = ('stock_item', 'change_type', 'old_quantity', 'new_quantity', 
                      'changed_by', 'created_at', 'note')
    
    def stock_item_name(self, obj):
        product_name = obj.stock_item.product.name if hasattr(obj.stock_item.product, 'name') else str(obj.stock_item.product)
        warehouse_name = obj.stock_item.warehouse.name
        return f"{product_name} - {warehouse_name}"
    stock_item_name.short_description = _('Stock Item')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Register the models
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(StockItem, StockItemAdmin)
admin.site.register(StockMovement, StockMovementAdmin)
admin.site.register(InventoryAuditLog, InventoryAuditLogAdmin)