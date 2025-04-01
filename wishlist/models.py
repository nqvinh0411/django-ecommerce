from django.db import models
from django.utils.translation import gettext_lazy as _
from customers.models import Customer
from products.models import Product


class Wishlist(models.Model):
    """
    Wishlist model to store customer's favorite products.
    Each customer can have only one wishlist.
    """
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name=_('Customer')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')

    def __str__(self):
        return f"Wishlist of {self.customer.user.email}"


class WishlistItem(models.Model):
    """
    WishlistItem model to store products in a customer's wishlist.
    """
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Wishlist')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name=_('Product')
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        # Ensure a product can only be added once to a wishlist
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist}"
