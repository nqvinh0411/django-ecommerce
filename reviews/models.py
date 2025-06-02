from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User
from products.models import Product

class Review(models.Model):
    """
    Model representing a product review by a user.
    Each user can only review a product once.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='User'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Product'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating',
        help_text='Rating from 1 to 5 stars'
    )
    comment = models.TextField(
        max_length=2000,
        blank=True,
        verbose_name='Comment',
        help_text='Review comment (optional)'
    )
    
    # Review status
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Approved',
        help_text='Whether the review is approved for display'
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name='Verified Purchase',
        help_text='Whether this review is from a verified purchase'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    # Admin moderation
    moderated_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Moderated At'
    )
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews',
        verbose_name='Moderated By'
    )
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}/5)"
    
    @property
    def rating_display(self):
        """Display rating as stars"""
        return '⭐' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def can_edit(self):
        """Check if review can be edited (within 24 hours of creation)"""
        if not self.created_at:
            return False
        return (timezone.now() - self.created_at).days < 1
    
    def save(self, *args, **kwargs):
        # Auto-detect verified purchase if order exists
        if not self.pk:  # Only on creation
            try:
                from orders.models import Order, OrderItem
                verified = OrderItem.objects.filter(
                    order__user=self.user,
                    product=self.product,
                    order__status__in=['completed', 'delivered']
                ).exists()
                self.is_verified_purchase = verified
            except ImportError:
                pass  # Orders app might not be available
        
        super().save(*args, **kwargs)
        
        # Update product average rating
        self.update_product_rating()
    
    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        
        # Update product rating after deletion
        self.update_product_rating_for_product(product)
    
    def update_product_rating(self):
        """Update average rating for the product"""
        self.update_product_rating_for_product(self.product)
    
    @staticmethod
    def update_product_rating_for_product(product):
        """Update average rating for a specific product"""
        from django.db.models import Avg
        
        avg_rating = Review.objects.filter(
            product=product,
            is_approved=True
        ).aggregate(avg_rating=Avg('rating'))['avg_rating']
        
        # Update product rating (assuming product has rating field)
        if hasattr(product, 'rating'):
            product.rating = avg_rating or 0
            product.save(update_fields=['rating'])
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('user', 'product')  # One review per user per product
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['rating']),
        ]
