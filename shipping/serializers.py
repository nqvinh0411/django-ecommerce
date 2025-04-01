from rest_framework import serializers
from .models import ShippingMethod, ShippingZone, ShippingRate, Shipment, TrackingInfo


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for ShippingMethod model"""
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'estimated_days', 'base_fee', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingZoneSerializer(serializers.ModelSerializer):
    """Serializer for ShippingZone model"""
    countries_list = serializers.SerializerMethodField()
    provinces_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ShippingZone
        fields = ['id', 'name', 'countries', 'provinces', 'countries_list', 
                 'provinces_list', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_countries_list(self, obj):
        return obj.get_countries_list()
        
    def get_provinces_list(self, obj):
        return obj.get_provinces_list()


class ShippingRateSerializer(serializers.ModelSerializer):
    """Serializer for ShippingRate model"""
    shipping_method_name = serializers.StringRelatedField(source='shipping_method')
    shipping_zone_name = serializers.StringRelatedField(source='shipping_zone')
    
    class Meta:
        model = ShippingRate
        fields = ['id', 'shipping_method', 'shipping_method_name', 
                 'shipping_zone', 'shipping_zone_name', 'min_weight', 
                 'max_weight', 'price', 'currency', 'is_active',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrackingInfoSerializer(serializers.ModelSerializer):
    """Serializer for TrackingInfo model"""
    class Meta:
        model = TrackingInfo
        fields = ['id', 'shipment', 'status', 'location', 'timestamp', 'note']
        read_only_fields = ['id', 'timestamp']


class OrderNestedSerializer(serializers.Serializer):
    """Simple serializer for Order model nested in Shipment"""
    id = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, required=False)
    status = serializers.CharField(read_only=True, required=False)
    
    # Use StringRelatedField if you're just showing the string representation
    customer = serializers.StringRelatedField(read_only=True, required=False)
    
    class Meta:
        fields = ['id', 'total', 'status', 'customer']


class ShipmentSerializer(serializers.ModelSerializer):
    """Serializer for Shipment model"""
    order = OrderNestedSerializer(read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)
    shipping_method_id = serializers.PrimaryKeyRelatedField(
        queryset=ShippingMethod.objects.all(),
        source='shipping_method',
        write_only=True
    )
    tracking_info = TrackingInfoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_shipment_status_display', read_only=True)
    
    class Meta:
        model = Shipment
        fields = ['id', 'order', 'shipping_method', 'shipping_method_id', 
                 'tracking_code', 'shipment_status', 'status_display',
                 'shipped_at', 'delivered_at', 'shipping_address',
                 'notes', 'created_at', 'updated_at', 'tracking_info']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Extract the order from context if it's provided
        order = self.context.get('order', None)
        if order:
            validated_data['order'] = order
            
        return super().create(validated_data)


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Shipment with minimal fields"""
    class Meta:
        model = Shipment
        fields = ['order', 'shipping_method', 'tracking_code', 
                 'shipment_status', 'shipped_at', 'shipping_address', 'notes']


class TrackingInfoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TrackingInfo"""
    class Meta:
        model = TrackingInfo
        fields = ['shipment', 'status', 'location', 'note']
    
    def create(self, validated_data):
        # Extract the shipment from context if it's provided
        shipment = self.context.get('shipment', None)
        if shipment:
            validated_data['shipment'] = shipment
            
        return super().create(validated_data)