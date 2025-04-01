from django.db.models.signals import post_save
from django.dispatch import receiver
from customers.models import Customer
from .models import Wishlist


@receiver(post_save, sender=Customer)
def create_customer_wishlist(sender, instance, created, **kwargs):
    """
    Signal to automatically create a wishlist when a new customer is created.
    This ensures every customer has a wishlist available immediately.
    """
    if created:
        Wishlist.objects.get_or_create(customer=instance)
