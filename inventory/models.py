from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Import Product model from products app
try:
    from products.models import Product
except ImportError:
    # If the Product model cannot be imported, create a placeholder for development
    Product = models.CharField(max_length=100)

# Import Order model from orders app
try:
    from orders.models import Order
except ImportError:
    # If the Order model cannot be imported, create a placeholder for development
    Order = models.CharField(max_length=100)


class Warehouse(models.Model):
    """
    Model for storing warehouse information
    """
    name = models.CharField(_("Warehouse Name"), max_length=100)
    location = models.CharField(_("Location"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    is_default = models.BooleanField(_("Default Warehouse"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If this warehouse is set as default, unset default for all other warehouses
        if self.is_default:
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        
        # If no warehouses exist or none is set as default, set this one as default
        if not self.pk and not Warehouse.objects.filter(is_default=True).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)


class StockItem(models.Model):
    """
    Model for storing stock information for products in warehouses
    """
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE,
        related_name='stock_items',
        verbose_name=_("Product")
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_items',
        verbose_name=_("Warehouse")
    )
    quantity = models.PositiveIntegerField(_("Quantity"), default=0)
    low_stock_threshold = models.PositiveIntegerField(_("Low Stock Threshold"), default=5)
    is_tracked = models.BooleanField(_("Track Inventory"), default=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Stock Item")
        verbose_name_plural = _("Stock Items")
        unique_together = ['product', 'warehouse']
        ordering = ['product__name', 'warehouse__name']

    def __str__(self):
        return f"{self.product} - {self.warehouse} ({self.quantity})"
    
    @property
    def is_low_stock(self):
        """Check if the item is below its low stock threshold"""
        return self.quantity <= self.low_stock_threshold and self.is_tracked


class StockMovement(models.Model):
    """
    Model for tracking stock movements (in, out, adjustments)
    """
    MOVEMENT_IN = 'IN'
    MOVEMENT_OUT = 'OUT'
    MOVEMENT_ADJUSTMENT = 'ADJUSTMENT'
    
    MOVEMENT_TYPE_CHOICES = [
        (MOVEMENT_IN, _('Stock In')),
        (MOVEMENT_OUT, _('Stock Out')),
        (MOVEMENT_ADJUSTMENT, _('Stock Adjustment')),
    ]
    
    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_("Stock Item")
    )
    movement_type = models.CharField(
        _("Movement Type"),
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES
    )
    quantity = models.IntegerField(_("Quantity"))
    reason = models.CharField(_("Reason"), max_length=255)
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements',
        verbose_name=_("Related Order")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements',
        verbose_name=_("Created By")
    )

    class Meta:
        verbose_name = _("Stock Movement")
        verbose_name_plural = _("Stock Movements")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.stock_item.product} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Create the movement record
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update stock item quantity only on creation (not on updates)
        if is_new:
            stock_item = self.stock_item
            
            # Track original quantity for the audit log
            old_quantity = stock_item.quantity
            
            # Update the stock item quantity based on movement type
            if self.movement_type == self.MOVEMENT_IN:
                stock_item.quantity += self.quantity
            elif self.movement_type == self.MOVEMENT_OUT:
                stock_item.quantity = max(0, stock_item.quantity - self.quantity)
            elif self.movement_type == self.MOVEMENT_ADJUSTMENT:
                stock_item.quantity = max(0, stock_item.quantity + self.quantity)
            
            stock_item.save()
            
            # Create audit log entry
            InventoryAuditLog.objects.create(
                stock_item=stock_item,
                change_type=f'MOVEMENT_{self.movement_type}',
                changed_by=self.created_by,
                old_quantity=old_quantity,
                new_quantity=stock_item.quantity,
                note=self.reason
            )


class InventoryAuditLog(models.Model):
    """
    Model for tracking all changes to inventory quantities
    """
    CHANGE_MOVEMENT_IN = 'MOVEMENT_IN'
    CHANGE_MOVEMENT_OUT = 'MOVEMENT_OUT'
    CHANGE_MOVEMENT_ADJUSTMENT = 'MOVEMENT_ADJUSTMENT'
    CHANGE_MANUAL = 'MANUAL'
    CHANGE_SYSTEM = 'SYSTEM'
    
    CHANGE_TYPE_CHOICES = [
        (CHANGE_MOVEMENT_IN, _('Stock Movement In')),
        (CHANGE_MOVEMENT_OUT, _('Stock Movement Out')),
        (CHANGE_MOVEMENT_ADJUSTMENT, _('Stock Movement Adjustment')),
        (CHANGE_MANUAL, _('Manual Change')),
        (CHANGE_SYSTEM, _('System Change')),
    ]
    
    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name=_("Stock Item")
    )
    change_type = models.CharField(
        _("Change Type"),
        max_length=30,
        choices=CHANGE_TYPE_CHOICES
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='inventory_changes',
        verbose_name=_("Changed By")
    )
    old_quantity = models.IntegerField(_("Old Quantity"))
    new_quantity = models.IntegerField(_("New Quantity"))
    note = models.TextField(_("Note"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Inventory Audit Log")
        verbose_name_plural = _("Inventory Audit Logs")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.stock_item.product} - {self.old_quantity} to {self.new_quantity} ({self.get_change_type_display()})"