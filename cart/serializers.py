from django.db.models import Sum
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework import serializers
from typing import Union
from decimal import Decimal

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer cho CartItem, hiển thị thông tin chi tiết của item trong giỏ hàng.
    """
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']
    
    def get_subtotal(self, obj: CartItem) -> Decimal:
        return obj.product.price * obj.quantity


class CartItemCreateSerializer(serializers.Serializer):
    """
    Serializer cho việc thêm sản phẩm vào giỏ hàng.
    """
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return value
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        return value


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer cho Cart, hiển thị thông tin giỏ hàng của người dùng.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_amount', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_total_items(self, obj: Cart) -> int:
        return obj.items.count()
    
    def get_total_amount(self, obj: Cart) -> Decimal:
        return sum(item.product.price * item.quantity for item in obj.items.all())
