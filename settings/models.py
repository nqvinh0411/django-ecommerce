from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


class StoreSetting(models.Model):
    """
    Stores global settings for the e-commerce platform.
    Only one instance of this model should exist.
    """
    store_name = models.CharField(max_length=255, verbose_name=_('Store Name'))
    store_logo = models.ImageField(
        upload_to='store/logo/',
        null=True,
        blank=True,
        verbose_name=_('Store Logo')
    )
    support_email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name=_('Support Email')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Address')
    )
    default_currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        null=True,
        related_name='store_settings',
        verbose_name=_('Default Currency')
    )
    default_language = models.ForeignKey(
        'LanguageSetting',
        on_delete=models.SET_NULL,
        null=True,
        related_name='store_settings',
        verbose_name=_('Default Language')
    )
    is_maintenance_mode = models.BooleanField(
        default=False,
        verbose_name=_('Maintenance Mode')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Store Setting')
        verbose_name_plural = _('Store Settings')

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        """
        Ensure only one instance of StoreSetting exists.
        If an instance already exists, update it instead of creating a new one.
        """
        if StoreSetting.objects.exists() and not self.pk:
            raise ValidationError(_('There can only be one store settings instance.'))
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """
        Get the store settings instance, creating it if it doesn't exist.
        """
        settings, created = cls.objects.get_or_create(
            defaults={
                'store_name': 'My E-Commerce Store',
                'support_email': 'support@example.com',
            }
        )
        return settings


class Currency(models.Model):
    """
    Model to store currencies supported by the store.
    """
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_('Currency Code')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Currency Name')
    )
    symbol = models.CharField(
        max_length=5,
        verbose_name=_('Currency Symbol')
    )
    exchange_rate_to_base = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=1.0,
        verbose_name=_('Exchange Rate to Base Currency')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Is Default Currency')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ['-is_default', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """
        Ensure only one default currency exists.
        """
        if self.is_default:
            # Set is_default=False for all other currencies
            Currency.objects.filter(is_default=True).update(is_default=False)
        # If no default currency exists, set this one as default
        elif not self.pk and not Currency.objects.filter(is_default=True).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)
        
        # Update StoreSetting if it exists and uses this currency
        if self.is_default:
            StoreSetting.objects.update(default_currency=self)


class LanguageSetting(models.Model):
    """
    Model to store languages supported by the store.
    """
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Language Code')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Language Name')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Is Default Language')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    class Meta:
        verbose_name = _('Language Setting')
        verbose_name_plural = _('Language Settings')
        ordering = ['-is_default', 'code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        """
        Ensure only one default language exists.
        """
        if self.is_default:
            # Set is_default=False for all other languages
            LanguageSetting.objects.filter(is_default=True).update(is_default=False)
        # If no default language exists, set this one as default
        elif not self.pk and not LanguageSetting.objects.filter(is_default=True).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)
        
        # Update StoreSetting if it exists and uses this language
        if self.is_default:
            StoreSetting.objects.update(default_language=self)


class EmailTemplate(models.Model):
    """
    Model to store email templates used by the system.
    """
    template_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Template Key')
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('Email Subject')
    )
    body_html = models.TextField(
        verbose_name=_('HTML Body')
    )
    body_text = models.TextField(
        verbose_name=_('Text Body')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
        ordering = ['template_key']

    def __str__(self):
        return self.template_key

    @staticmethod
    def get_template(template_key):
        """
        Get an email template by its key.
        """
        try:
            return EmailTemplate.objects.get(template_key=template_key, is_active=True)
        except EmailTemplate.DoesNotExist:
            return None
