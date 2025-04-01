from rest_framework import serializers
from .models import Warehouse, StockItem, StockMovement, InventoryAuditLog


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model"""
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'description', 'is_default', 'is_active', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductNestedSerializer(serializers.Serializer):
    """Simple nested serializer for Product model"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    
    class Meta:
        fields = ['id', 'name']


class WarehouseNestedSerializer(serializers.ModelSerializer):
    """Simple nested serializer for Warehouse model"""
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location']


class StockItemSerializer(serializers.ModelSerializer):
    """Serializer for StockItem model with nested Product and Warehouse"""
    product = ProductNestedSerializer(read_only=True)
    warehouse = WarehouseNestedSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    warehouse_id = serializers.IntegerField(write_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StockItem
        fields = ['id', 'product', 'product_id', 'warehouse', 'warehouse_id', 
                 'quantity', 'low_stock_threshold', 'is_tracked', 'is_low_stock',
                 'last_updated', 'created_at']
        read_only_fields = ['last_updated', 'created_at']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    stock_item_id = serializers.IntegerField(write_only=True)
    stock_item = StockItemSerializer(read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    related_order_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    product_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = ['id', 'stock_item', 'stock_item_id', 'movement_type', 'movement_type_display',
                 'quantity', 'reason', 'related_order', 'related_order_id', 
                 'created_by', 'created_by_username', 'product_name', 'created_at']
        read_only_fields = ['created_at', 'created_by']
    
    def get_product_name(self, obj):
        """Get the product name from the stock item's product"""
        if hasattr(obj.stock_item.product, 'name'):
            return obj.stock_item.product.name
        return str(obj.stock_item.product)
    
    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user if 'request' in self.context else None
        
        # Add the user to created_by field
        if user and not user.is_anonymous:
            validated_data['created_by'] = user
            
        return super().create(validated_data)


class InventoryAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for InventoryAuditLog model"""
    stock_item = StockItemSerializer(read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = InventoryAuditLog
        fields = ['id', 'stock_item', 'change_type', 'change_type_display', 
                 'changed_by', 'changed_by_username', 'old_quantity', 'new_quantity', 
                 'note', 'created_at']
        read_only_fields = ['id', 'stock_item', 'change_type', 'changed_by', 
                           'old_quantity', 'new_quantity', 'created_at']