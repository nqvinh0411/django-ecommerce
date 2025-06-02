from django.db.models import Sum
from products.models import Product
from products.serializers import ProductSummarySerializer
from rest_framework import serializers
from typing import Union
from decimal import Decimal

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer cho CartItem, hiển thị thông tin chi tiết của item trong giỏ hàng.
    """
    product = ProductSummarySerializer(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    unit_price = serializers.SerializerMethodField(read_only=True)
    product_available = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'subtotal', 
            'product_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'subtotal', 'product_available', 'created_at', 'updated_at']
    
    def get_subtotal(self, obj: CartItem) -> Decimal:
        return obj.subtotal
    
    def get_unit_price(self, obj: CartItem) -> Decimal:
        return obj.product.price
    
    def get_product_available(self, obj: CartItem) -> bool:
        """Check if product is still available and in stock"""
        return hasattr(obj.product, 'stock') and obj.product.stock >= obj.quantity


class CartItemCreateSerializer(serializers.Serializer):
    """
    Serializer cho việc thêm sản phẩm vào giỏ hàng.
    """
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=False, default=1, min_value=1, max_value=999)
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            # Check if product is available (có thể thêm logic kiểm tra stock)
            # if hasattr(product, 'stock') and product.stock <= 0:
            #     raise serializers.ValidationError("Sản phẩm đã hết hàng")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return value
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        if value > 999:
            raise serializers.ValidationError("Số lượng không được quá 999")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
            # Check stock if product has stock field
            if hasattr(product, 'stock') and product.stock < quantity:
                raise serializers.ValidationError(
                    f"Chỉ còn {product.stock} sản phẩm trong kho"
                )
        except Product.DoesNotExist:
            pass  # Already handled in validate_product_id
        
        return data


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc cập nhật CartItem.
    """
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        if value > 999:
            raise serializers.ValidationError("Số lượng không được quá 999")
        
        # Check stock if available
        instance = self.instance
        if instance and hasattr(instance.product, 'stock'):
            if instance.product.stock < value:
                raise serializers.ValidationError(
                    f"Chỉ còn {instance.product.stock} sản phẩm trong kho"
                )
        
        return value


class CartSummarySerializer(serializers.ModelSerializer):
    """
    Serializer cho tóm tắt giỏ hàng (read-only).
    """
    item_count = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'item_count', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_item_count(self, obj: Cart) -> int:
        return obj.total_items
    
    def get_total_amount(self, obj: Cart) -> str:
        return str(obj.total_amount)


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho Cart, hiển thị thông tin giỏ hàng của người dùng.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    is_empty = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_email', 'items', 'total_items', 
            'total_amount', 'is_empty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'created_at', 'updated_at']
    
    def get_total_items(self, obj: Cart) -> int:
        return obj.total_items
    
    def get_total_amount(self, obj: Cart) -> Decimal:
        return obj.total_amount
    
    def get_is_empty(self, obj: Cart) -> bool:
        return obj.is_empty


class CartCheckoutSerializer(serializers.Serializer):
    """
    Serializer cho việc checkout giỏ hàng.
    """
    shipping_address = serializers.CharField(max_length=500, required=True)
    billing_address = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Địa chỉ giao hàng là bắt buộc")
        return value.strip()
    
    def validate(self, data):
        """Validate cart has items before checkout"""
        request = self.context.get('request')
        if request and request.user:
            try:
                cart = Cart.objects.get(user=request.user)
                if cart.is_empty:
                    raise serializers.ValidationError("Giỏ hàng đang trống")
            except Cart.DoesNotExist:
                raise serializers.ValidationError("Không tìm thấy giỏ hàng")
        
        return data
