from rest_framework import serializers
from customers.serializers import CustomerSerializer
from products.serializers import ProductSerializer
from .models import SalesReport, ProductReport, CustomerReport, TrafficLog


class SalesReportSerializer(serializers.ModelSerializer):
    """
    Serializer for SalesReport model - read-only.
    """
    class Meta:
        model = SalesReport
        fields = [
            'id', 'date', 'total_orders', 'total_revenue',
            'total_discount', 'net_revenue', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ProductReportSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductReport model - read-only with product details.
    """
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = ProductReport
        fields = [
            'id', 'product', 'sold_quantity', 'total_revenue',
            'average_rating', 'last_sold_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class CustomerReportSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerReport model - read-only with customer details.
    """
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = CustomerReport
        fields = [
            'id', 'customer', 'total_orders', 'total_spent',
            'average_order_value', 'last_order_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class TrafficLogSerializer(serializers.ModelSerializer):
    """
    Serializer for TrafficLog model - read-only.
    """
    class Meta:
        model = TrafficLog
        fields = [
            'id', 'endpoint', 'method', 'ip_address',
            'user_agent', 'duration_ms', 'timestamp'
        ]
        read_only_fields = fields
