from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Page(models.Model):
    """
    Model for static content pages like About Us, Privacy Policy, etc.
    """
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_('URL Slug')
    )
    content_html = models.TextField(verbose_name=_('HTML Content'))
    content_text = models.TextField(
        blank=True,
        help_text=_('Plain text version for SEO and accessibility'),
        verbose_name=_('Text Content')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published')
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Published At')
    )
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text=_('SEO optimized title (max 70 characters)'),
        verbose_name=_('SEO Title')
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        help_text=_('Meta description for SEO (max 160 characters)'),
        verbose_name=_('SEO Description')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Banner(models.Model):
    """
    Model for promotional banners displayed on various parts of the site.
    """
    POSITION_CHOICES = [
        ('homepage_top', _('Homepage Top')),
        ('homepage_middle', _('Homepage Middle')),
        ('homepage_bottom', _('Homepage Bottom')),
        ('footer', _('Footer')),
        ('sidebar', _('Sidebar')),
        ('category_page', _('Category Page')),
        ('product_page', _('Product Page')),
    ]

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    image = models.ImageField(
        upload_to='banners/',
        verbose_name=_('Banner Image')
    )
    link_url = models.URLField(
        blank=True,
        verbose_name=_('Link URL')
    )
    position = models.CharField(
        max_length=30,
        choices=POSITION_CHOICES,
        verbose_name=_('Position')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Start Date')
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """Check if banner has expired based on end_date"""
        if self.end_date and timezone.now() > self.end_date:
            return True
        return False


class MenuItem(models.Model):
    """
    Model for navigation menu items with hierarchical structure.
    """
    MENU_TYPE_CHOICES = [
        ('header', _('Header Menu')),
        ('footer', _('Footer Menu')),
        ('mobile', _('Mobile Menu')),
        ('sidebar', _('Sidebar Menu')),
        ('account', _('Account Menu')),
    ]

    label = models.CharField(max_length=100, verbose_name=_('Label'))
    url = models.CharField(
        max_length=255,
        verbose_name=_('URL'),
        help_text=_('URL path or absolute link')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent Menu Item')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    menu_type = models.CharField(
        max_length=20,
        choices=MENU_TYPE_CHOICES,
        verbose_name=_('Menu Type')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Menu Item')
        verbose_name_plural = _('Menu Items')
        ordering = ['menu_type', 'order']

    def __str__(self):
        return f"{self.label} ({self.get_menu_type_display()})"

    @property
    def has_children(self):
        """Check if menu item has children"""
        return self.children.filter(is_active=True).exists()
