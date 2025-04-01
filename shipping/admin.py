from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ShippingMethod, ShippingZone, ShippingRate, Shipment, TrackingInfo


class ShippingRateInline(admin.TabularInline):
    model = ShippingRate
    extra = 1
    fields = ('shipping_zone', 'min_weight', 'max_weight', 'price', 'currency', 'is_active')


class TrackingInfoInline(admin.TabularInline):
    model = TrackingInfo
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('status', 'location', 'timestamp', 'note')
    max_num = 10
    can_delete = False


class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'estimated_days', 'base_fee', 'is_active', 'created_at')
    list_filter = ('is_active', 'estimated_days')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'estimated_days', 'base_fee')
    inlines = [ShippingRateInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Shipping Details'), {
            'fields': ('estimated_days', 'base_fee', 'is_active')
        }),
    )


class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'countries_display', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'countries', 'provinces')
    list_editable = ('is_active',)
    inlines = [ShippingRateInline]
    
    def countries_display(self, obj):
        return obj.countries
    countries_display.short_description = _('Countries')


class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('shipping_method', 'shipping_zone', 'weight_range', 'price', 'currency', 'is_active')
    list_filter = ('shipping_method', 'shipping_zone', 'is_active', 'currency')
    search_fields = ('shipping_method__name', 'shipping_zone__name')
    list_editable = ('price', 'is_active')
    
    def weight_range(self, obj):
        return f"{obj.min_weight} - {obj.max_weight} kg"
    weight_range.short_description = _('Weight Range (kg)')


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_info', 'shipping_method', 'shipment_status', 
                   'tracking_code', 'shipped_at', 'delivered_at', 'created_at')
    list_filter = ('shipment_status', 'shipping_method', 'shipped_at', 'delivered_at')
    search_fields = ('order__id', 'tracking_code', 'notes', 'shipping_address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TrackingInfoInline]
    fieldsets = (
        (None, {
            'fields': ('order', 'shipping_method')
        }),
        (_('Shipment Details'), {
            'fields': ('shipment_status', 'tracking_code', 'shipping_address', 'notes')
        }),
        (_('Dates'), {
            'fields': ('shipped_at', 'delivered_at', 'created_at', 'updated_at')
        }),
    )
    
    def order_info(self, obj):
        if hasattr(obj.order, 'id'):
            return f"Order #{obj.order.id}"
        return str(obj.order)
    order_info.short_description = _('Order')


class TrackingInfoAdmin(admin.ModelAdmin):
    list_display = ('shipment_ref', 'status', 'location', 'timestamp', 'note')
    list_filter = ('status', 'timestamp', 'shipment__shipment_status')
    search_fields = ('status', 'location', 'note', 'shipment__tracking_code')
    readonly_fields = ('timestamp',)
    
    def shipment_ref(self, obj):
        return f"Shipment #{obj.shipment.id} ({obj.shipment.tracking_code})"
    shipment_ref.short_description = _('Shipment')


# Register the models with the custom admin classes
admin.site.register(ShippingMethod, ShippingMethodAdmin)
admin.site.register(ShippingZone, ShippingZoneAdmin)
admin.site.register(ShippingRate, ShippingRateAdmin)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(TrackingInfo, TrackingInfoAdmin)