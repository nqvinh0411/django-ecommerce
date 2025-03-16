from django.db import models
from products.models import Product
from setuptools.package_index import user_agent
from users.models import User

STATUS_CHOICES = [
    ('PENDING', 'PENDING'),
    ('SHIPPED', 'SHIPPED'),
    ('DELIVERED', 'DELIVERED'),
    ('CANCELED', 'CANCELED'),
]


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
