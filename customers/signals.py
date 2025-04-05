from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Create a Customer instance for every new User
    """
    if created and getattr(instance, 'is_customer', False):
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """
    Save the Customer instance every time the User is saved
    """
    if hasattr(instance, 'customer'):
        instance.customer.save()
