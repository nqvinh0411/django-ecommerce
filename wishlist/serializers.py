from rest_framework import serializers
from products.serializers import ProductSummarySerializer
from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for WishlistItem model with nested product information.
    """
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='product',
        queryset=WishlistItem.product.field.related_model.objects.all(),
        error_messages={
            'does_not_exist': 'The specified product does not exist.',
            'invalid': 'Invalid product ID format.'
        }
    )

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id', 'added_at']
        read_only_fields = ['id', 'added_at']
        
    def validate_product_id(self, value):
        """
        Validate that the product exists and is active.
        """
        if hasattr(value, 'is_active') and not value.is_active:
            raise serializers.ValidationError("This product is no longer available.")
        return value
        
    def validate(self, attrs):
        """
        Custom validation for the entire serializer.
        """
        # Add any additional cross-field validation if needed
        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for Wishlist model with nested items.
    """
    items = WishlistItemSerializer(many=True, read_only=True, source='wishlist_items')
    total_items = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'created_at', 'updated_at', 'items', 'total_items']
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_items']
        
    def get_total_items(self, obj):
        """
        Get the total number of items in the wishlist.
        """
        return obj.wishlist_items.count() if hasattr(obj, 'wishlist_items') else 0
