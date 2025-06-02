from catalog.models import Category
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal
from users.models import User


class Product(models.Model):
    """
    Product model with seller management and user features.
    """
    PRODUCT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]
    
    # Basic product info
    name = models.CharField(max_length=255, verbose_name='Product Name')
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='URL Slug')
    description = models.TextField(verbose_name='Description')
    short_description = models.TextField(
        max_length=500, 
        blank=True,
        verbose_name='Short Description',
        help_text='Brief description for product lists'
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Price'
    )
    compare_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Compare Price',
        help_text='Original price for discount display'
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Cost Price',
        help_text='Internal cost price (seller only)'
    )
    
    # Inventory
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock Quantity'
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name='Low Stock Alert Threshold'
    )
    track_inventory = models.BooleanField(
        default=True,
        verbose_name='Track Inventory'
    )
    
    # Product organization
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products',
        verbose_name='Category'
    )
    sku = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True,
        verbose_name='SKU',
        help_text='Stock Keeping Unit'
    )
    barcode = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Barcode'
    )
    
    # Seller info
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Seller'
    )
    
    # Product status
    status = models.CharField(
        max_length=20,
        choices=PRODUCT_STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Featured Product'
    )
    is_digital = models.BooleanField(
        default=False,
        verbose_name='Digital Product'
    )
    
    # SEO and metadata
    meta_title = models.CharField(
        max_length=160, 
        blank=True,
        verbose_name='Meta Title'
    )
    meta_description = models.CharField(
        max_length=320, 
        blank=True,
        verbose_name='Meta Description'
    )
    
    # Analytics fields
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Views Count'
    )
    sales_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Sales Count'
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Average Rating'
    )
    reviews_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Reviews Count'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Published At')
    
    # Weight and dimensions
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Weight (kg)'
    )
    length = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Length (cm)'
    )
    width = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Width (cm)'
    )
    height = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Height (cm)'
    )

    def __str__(self):
        return f"{self.name} ({self.seller.email})"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Auto-generate SKU if not provided
        if not self.sku:
            # Generate SKU based on seller ID and product name
            import uuid
            self.sku = f"SKU-{self.seller.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Set published_at when status changes to active
        if self.status == 'active' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.stock <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price exists"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 1)
        return 0
    
    @property
    def primary_image(self):
        """Get primary product image"""
        return self.images.filter(is_primary=True).first()
    
    def increment_views(self):
        """Increment product views count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def update_rating(self):
        """Update average rating from reviews"""
        from django.db.models import Avg
        try:
            from reviews.models import Review
            avg_rating = Review.objects.filter(
                product=self, 
                is_approved=True
            ).aggregate(avg_rating=Avg('rating'))['avg_rating']
            
            reviews_count = Review.objects.filter(
                product=self, 
                is_approved=True
            ).count()
            
            self.rating = avg_rating or 0
            self.reviews_count = reviews_count
            self.save(update_fields=['rating', 'reviews_count'])
        except ImportError:
            pass  # Reviews app not available
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
        ]


class ProductImage(models.Model):
    """
    Product image model with enhanced metadata.
    """
    product = models.ForeignKey(
        Product, 
        related_name='images', 
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    image = models.ImageField(
        upload_to='products/images/',
        verbose_name='Image'
    )
    alt_text = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Alt Text'
    )
    caption = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Caption'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Primary Image'
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Sort Order'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order', 'created_at']


class ProductFavorite(models.Model):
    """
    User favorite products model.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_products',
        verbose_name='User'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Product'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added At')
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    
    class Meta:
        verbose_name = 'Product Favorite'
        verbose_name_plural = 'Product Favorites'
        unique_together = ('user', 'product')
        ordering = ['-created_at']


class ProductView(models.Model):
    """
    Track product views by users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_views',
        verbose_name='User'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_views',
        verbose_name='Product'
    )
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='Viewed At')
    
    def __str__(self):
        user_info = self.user.email if self.user else f"Anonymous ({self.ip_address})"
        return f"{user_info} viewed {self.product.name}"
    
    class Meta:
        verbose_name = 'Product View'
        verbose_name_plural = 'Product Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['product', 'viewed_at']),
        ]
