from django.db import models
from django.utils.translation import gettext_lazy as _
from customers.models import Customer
from products.models import Product


class SalesReport(models.Model):
    """
    Model for daily sales reports summarizing order metrics.
    """
    date = models.DateField(unique=True, verbose_name=_('Date'))
    total_orders = models.PositiveIntegerField(default=0, verbose_name=_('Total Orders'))
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Revenue')
    )
    total_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Discount')
    )
    net_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Net Revenue')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sales Report')
        verbose_name_plural = _('Sales Reports')
        ordering = ['-date']

    def __str__(self):
        return f"Sales Report {self.date}"


class ProductReport(models.Model):
    """
    Model for product-specific performance metrics.
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name=_('Product')
    )
    sold_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Sold Quantity'))
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Revenue')
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name=_('Average Rating')
    )
    last_sold_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Sold At')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product Report')
        verbose_name_plural = _('Product Reports')
        ordering = ['-sold_quantity']

    def __str__(self):
        return f"Report for {self.product.name}"


class CustomerReport(models.Model):
    """
    Model for customer-specific performance metrics.
    """
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name=_('Customer')
    )
    total_orders = models.PositiveIntegerField(default=0, verbose_name=_('Total Orders'))
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Spent')
    )
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Average Order Value')
    )
    last_order_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Order At')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer Report')
        verbose_name_plural = _('Customer Reports')
        ordering = ['-total_spent']

    def __str__(self):
        return f"Report for {self.customer.user.email}"


class TrafficLog(models.Model):
    """
    Model for tracking API traffic and performance.
    """
    endpoint = models.CharField(max_length=255, verbose_name=_('Endpoint'))
    method = models.CharField(max_length=10, verbose_name=_('HTTP Method'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    duration_ms = models.PositiveIntegerField(verbose_name=_('Duration (ms)'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Traffic Log')
        verbose_name_plural = _('Traffic Logs')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.duration_ms}ms"
