from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """
    Enhanced User model với role management và profile fields.
    """
    # Role fields
    is_seller = models.BooleanField(
        default=False,
        verbose_name='Is Seller',
        help_text='User can sell products'
    )
    is_customer = models.BooleanField(
        default=True,
        verbose_name='Is Customer', 
        help_text='User can buy products'
    )
    
    # Profile fields
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be valid format"
        )],
        verbose_name='Phone Number'
    )
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Address'
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Date of Birth'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    
    # Account status
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verified'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Account'
    )
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name='Last Login IP'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    # Fix related_name conflicts
    groups = models.ManyToManyField(
        Group, 
        related_name="custom_user_groups", 
        blank=True,
        verbose_name='Groups'
    )
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="custom_user_permissions", 
        blank=True,
        verbose_name='User Permissions'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_seller', 'is_customer']),
        ]
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def display_name(self):
        """Get user's display name for UI"""
        return self.full_name or self.email or self.username
    
    def get_role_display(self):
        """Get user role as string"""
        roles = []
        if self.is_staff:
            roles.append('Admin')
        if self.is_seller:
            roles.append('Seller')
        if self.is_customer:
            roles.append('Customer')
        return ', '.join(roles) if roles else 'User'
