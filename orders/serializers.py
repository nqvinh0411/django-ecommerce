from products.serializers import ProductSerializer
from rest_framework import serializers
from django.db.models import Sum
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=ProductSerializer.Meta.model.objects.all(),
        write_only=True
    )
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    items_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'status', 'status_display', 
                 'total_amount', 'items_count', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'user', 'user_email', 'created_at', 'updated_at', 
                           'status_display', 'total_amount', 'items_count']
    
    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
    
    def get_status_display(self, obj):
        status_choices = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý', 
            'shipped': 'Đã giao cho đơn vị vận chuyển',
            'delivered': 'Đã giao hàng',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_choices.get(obj.status, obj.status)
    
    def get_total_amount(self, obj):
        return obj.items.aggregate(total=Sum('price', field='price*quantity'))['total'] or 0
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Trạng thái không hợp lệ. Các trạng thái hợp lệ: {', '.join(valid_statuses)}"
            )
        return value
