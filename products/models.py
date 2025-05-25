from catalog.models import Category
from django.db import models
from users.models import User


class Product(models.Model):
    name = models.CharField(max_length=2550)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.CharField(max_length=2550)  # Thêm max_length để khắc phục lỗi
    created_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=2550, blank=True)

    def __str__(self):
        return self.product.name
