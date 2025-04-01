from rest_framework import serializers
from products.serializers import ProductSerializer
from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for WishlistItem model with nested product information.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='product',
        queryset=WishlistItem.product.field.related_model.objects.all()
    )

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id', 'added_at']
        read_only_fields = ['id', 'added_at']


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for Wishlist model with nested items.
    """
    items = WishlistItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'created_at', 'items']
        read_only_fields = ['id', 'created_at']
