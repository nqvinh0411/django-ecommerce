from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class CustomerGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount rate in percentage (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Discount: {self.discount_rate}%)"

    class Meta:
        ordering = ['name']

class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    group = models.ForeignKey(
        CustomerGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers'
    )
    loyalty_points = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.group.name if self.group else 'No Group'}"

    class Meta:
        ordering = ['-created_at']

class CustomerAddress(models.Model):
    ADDRESS_TYPES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
        ('both', 'Both')
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(
        max_length=8,
        choices=ADDRESS_TYPES,
        default='both'
    )
    is_default = models.BooleanField(default=False)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.user.email} - {self.street_address}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of same type to non-default
            CustomerAddress.objects.filter(
                customer=self.customer,
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Customer addresses'

class CustomerActivity(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.email} - {self.activity_type} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Customer activities'
