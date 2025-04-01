from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

# Import Order model from orders app
try:
    from orders.models import Order
except ImportError:
    # If the Order model cannot be imported, create a placeholder for development
    Order = models.CharField(max_length=100)


class ShippingMethod(models.Model):
    """
    Shipping methods available for delivery (e.g. Standard, Express, Next Day)
    """
    name = models.CharField(_("Method Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    estimated_days = models.PositiveIntegerField(_("Estimated Delivery Days"), default=3)
    base_fee = models.DecimalField(_("Base Fee"), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Shipping Method")
        verbose_name_plural = _("Shipping Methods")
        ordering = ['name']

    def __str__(self):
        return self.name


class ShippingZone(models.Model):
    """
    Geographical regions for shipping (e.g. Domestic, Europe, Asia)
    """
    name = models.CharField(_("Zone Name"), max_length=100)
    countries = models.TextField(_("Countries"), 
                               help_text=_("Comma-separated list of country codes (e.g. 'VN,TH,SG')"))
    provinces = models.TextField(_("Provinces/States"), 
                               help_text=_("Comma-separated list of provinces/states (can be empty)"),
                               blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Shipping Zone")
        verbose_name_plural = _("Shipping Zones")
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_countries_list(self):
        """Returns list of country codes"""
        if not self.countries:
            return []
        return [c.strip() for c in self.countries.split(',')]

    def get_provinces_list(self):
        """Returns list of provinces"""
        if not self.provinces:
            return []
        return [p.strip() for p in self.provinces.split(',')]


class ShippingRate(models.Model):
    """
    Specific pricing for a shipping method in a particular zone based on weight
    """
    shipping_method = models.ForeignKey(
        ShippingMethod, 
        on_delete=models.CASCADE,
        related_name='rates',
        verbose_name=_("Shipping Method")
    )
    shipping_zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='rates',
        verbose_name=_("Shipping Zone")
    )
    min_weight = models.DecimalField(_("Minimum Weight (kg)"), max_digits=8, decimal_places=2, default=0)
    max_weight = models.DecimalField(_("Maximum Weight (kg)"), max_digits=8, decimal_places=2, default=999)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default='VND')
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Shipping Rate")
        verbose_name_plural = _("Shipping Rates")
        ordering = ['shipping_method', 'shipping_zone', 'min_weight']
        unique_together = [['shipping_method', 'shipping_zone', 'min_weight', 'max_weight']]

    def __str__(self):
        return f"{self.shipping_method} - {self.shipping_zone} ({self.min_weight}kg to {self.max_weight}kg)"


class Shipment(models.Model):
    """
    A shipment record associated with an order
    """
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_DELIVERED = 'delivered'
    STATUS_RETURNED = 'returned'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_SHIPPED, _('Shipped')),
        (STATUS_IN_TRANSIT, _('In Transit')),
        (STATUS_DELIVERED, _('Delivered')),
        (STATUS_RETURNED, _('Returned')),
        (STATUS_FAILED, _('Failed')),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name=_("Order")
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.PROTECT,
        related_name='shipments',
        verbose_name=_("Shipping Method")
    )
    tracking_code = models.CharField(_("Tracking Code"), max_length=100, blank=True)
    shipment_status = models.CharField(
        _("Shipment Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    shipped_at = models.DateTimeField(_("Shipped At"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Delivered At"), null=True, blank=True)
    shipping_address = models.TextField(_("Shipping Address"), blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment #{self.id} - Order #{self.order.id if hasattr(self.order, 'id') else self.order}"
    
    @property
    def last_tracking_info(self):
        """Returns the most recent tracking info"""
        return self.tracking_info.order_by('-timestamp').first()


class TrackingInfo(models.Model):
    """
    Tracking information updates for shipments
    """
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='tracking_info',
        verbose_name=_("Shipment")
    )
    status = models.CharField(_("Status"), max_length=100)
    location = models.CharField(_("Location"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    note = models.TextField(_("Note"), blank=True)

    class Meta:
        verbose_name = _("Tracking Information")
        verbose_name_plural = _("Tracking Information")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.status} at {self.location} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"