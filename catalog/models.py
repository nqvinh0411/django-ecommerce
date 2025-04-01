from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Product category with hierarchical structure support.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category-detail', kwargs={'slug': self.slug})

    @property
    def get_descendants(self):
        """Returns all descendants of this category"""
        descendants = []
        children = self.children.all()
        
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants)
            
        return descendants


class Brand(models.Model):
    """
    Product brand information model.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:brand-detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Product tag model.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:tag-detail', kwargs={'slug': self.slug})


class Attribute(models.Model):
    """
    Product attribute model for dynamic attributes.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_filterable = models.BooleanField(default=True, help_text="Can be used for filtering products")
    is_variant = models.BooleanField(default=False, help_text="Used for product variants")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:attribute-detail', kwargs={'slug': self.slug})


class AttributeValue(models.Model):
    """
    Product attribute value linked to an Attribute.
    """
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, 
        related_name='values'
    )
    value = models.CharField(max_length=255)
    display_value = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['attribute', 'value']
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.value)
        
        if not self.display_value:
            self.display_value = self.value
            
        super().save(*args, **kwargs)