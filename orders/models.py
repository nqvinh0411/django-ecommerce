from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from users.models import User


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


class Order(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='User'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Status'
    )
    
    # Order tracking
    order_number = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True,
        verbose_name='Order Number'
    )
    
    # Totals
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Tax Amount'
    )
    shipping_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Shipping Amount'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total Amount'
    )
    
    # Shipping information
    shipping_address = models.TextField(blank=True, verbose_name='Shipping Address')
    billing_address = models.TextField(blank=True, verbose_name='Billing Address')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='Shipped At')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Delivered At')
    
    # Notes
    notes = models.TextField(blank=True, verbose_name='Notes')
    admin_notes = models.TextField(blank=True, verbose_name='Admin Notes')

    def __str__(self):
        return f"Order #{self.order_number or self.id} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Auto-generate order number if not provided
        if not self.order_number:
            # Generate order number based on ID and timestamp
            # This will be updated after save to include the ID
            pass
        super().save(*args, **kwargs)
        
        # Generate order number after save to include ID
        if not self.order_number:
            self.order_number = f"ORD-{self.created_at.strftime('%Y%m%d')}-{self.id:06d}"
            super().save(update_fields=['order_number'])

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Order'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantity'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Unit Price'
    )
    
    # Product snapshot data at time of order
    product_name = models.CharField(max_length=255, verbose_name='Product Name')
    product_sku = models.CharField(max_length=100, blank=True, verbose_name='Product SKU')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    def __str__(self):
        return f"{self.product_name} x {self.quantity} - {self.order}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        # Snapshot product data
        if self.product and not self.product_name:
            self.product_name = self.product.name
            # Add SKU if product has it
            # self.product_sku = getattr(self.product, 'sku', '')
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['id']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
