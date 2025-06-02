from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from users.models import User


class Cart(models.Model):
    """
    Model representing a shopping cart for a user.
    Each user has one cart that persists across sessions.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='User'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    # Session tracking for potential future use
    session_key = models.CharField(
        max_length=40, 
        blank=True, 
        null=True,
        help_text="Session key for anonymous users"
    )
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def total_amount(self):
        """Total amount of all items in cart"""
        total = Decimal('0.00')
        for item in self.items.select_related('product').all():
            total += item.subtotal
        return total
    
    @property
    def is_empty(self):
        """Check if cart is empty"""
        return not self.items.exists()
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()
    
    def add_item(self, product, quantity=1):
        """
        Add item to cart or update quantity if exists.
        
        Args:
            product: Product instance
            quantity: Quantity to add (default: 1)
            
        Returns:
            CartItem: The created or updated cart item
        """
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_item(self, product):
        """
        Remove item from cart completely.
        
        Args:
            product: Product instance to remove
        """
        self.items.filter(product=product).delete()
    
    def update_item_quantity(self, product, quantity):
        """
        Update item quantity in cart.
        
        Args:
            product: Product instance
            quantity: New quantity
            
        Returns:
            CartItem or None: Updated cart item or None if quantity is 0
        """
        try:
            cart_item = self.items.get(product=product)
            if quantity <= 0:
                cart_item.delete()
                return None
            else:
                cart_item.quantity = quantity
                cart_item.save()
                return cart_item
        except CartItem.DoesNotExist:
            return None
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']


class CartItem(models.Model):
    """
    Model representing an item in a shopping cart.
    """
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cart'
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
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.cart.user.email}'s cart"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.product.price * self.quantity
    
    def save(self, *args, **kwargs):
        # Update cart's updated_at when cart item changes
        super().save(*args, **kwargs)
        self.cart.save(update_fields=['updated_at'])
    
    def delete(self, *args, **kwargs):
        # Update cart's updated_at when cart item is deleted
        cart = self.cart
        super().delete(*args, **kwargs)
        cart.save(update_fields=['updated_at'])
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')  # Prevent duplicate products in same cart
        ordering = ['created_at']
