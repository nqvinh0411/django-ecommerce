from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from products.serializers import ProductSummarySerializer
from products.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer cho OrderItem, hiển thị thông tin item trong đơn hàng.
    """
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )
    subtotal = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'product_name', 'product_sku',
            'quantity', 'price', 'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_sku', 'subtotal', 'created_at']
    
    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer chính cho Order, sử dụng cho cả user và admin.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    items_count = serializers.SerializerMethodField(read_only=True)
    can_cancel = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'user_full_name',
            'status', 'status_display', 'subtotal', 'tax_amount', 
            'shipping_amount', 'total_amount', 'shipping_address',
            'billing_address', 'notes', 'items_count', 'can_cancel', 
            'can_edit', 'created_at', 'updated_at', 'shipped_at', 
            'delivered_at', 'items'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'user_email', 'user_full_name',
            'status_display', 'items_count', 'can_cancel', 'can_edit',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
    
    def get_user_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return None
    
    def get_status_display(self, obj):
        status_choices = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý', 
            'shipped': 'Đã gửi hàng',
            'delivered': 'Đã giao hàng',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_choices.get(obj.status, obj.status)
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_can_cancel(self, obj):
        """User có thể hủy đơn hàng nếu đang ở trạng thái pending hoặc processing"""
        return obj.status in ['pending', 'processing']
    
    def get_can_edit(self, obj):
        """User có thể chỉnh sửa đơn hàng nếu đang ở trạng thái pending"""
        return obj.status == 'pending'


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer để tạo đơn hàng mới từ giỏ hàng.
    """
    class Meta:
        model = Order
        fields = ['shipping_address', 'billing_address', 'notes']
    
    def validate_shipping_address(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Địa chỉ giao hàng là bắt buộc")
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer để cập nhật trạng thái đơn hàng (chủ yếu dành cho admin).
    """
    admin_notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Order
        fields = ['status', 'admin_notes']
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Trạng thái không hợp lệ. Các trạng thái hợp lệ: {', '.join(valid_statuses)}"
            )
        return value
    
    def validate(self, data):
        """Validate status transitions"""
        instance = self.instance
        if not instance:
            return data
            
        current_status = instance.status
        new_status = data.get('status', current_status)
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['completed'],
            'completed': [],  # Final state
            'cancelled': []   # Final state
        }
        
        if new_status != current_status:
            if new_status not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Không thể chuyển từ trạng thái '{current_status}' sang '{new_status}'"
                )
        
        return data


class OrderCancelSerializer(serializers.Serializer):
    """
    Serializer để hủy đơn hàng (cho user).
    """
    reason = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="Lý do hủy đơn hàng"
    )
    
    def validate(self, data):
        # User chỉ có thể hủy đơn hàng ở trạng thái pending hoặc processing
        order = self.context.get('order')
        if order and order.status not in ['pending', 'processing']:
            raise serializers.ValidationError(
                "Chỉ có thể hủy đơn hàng ở trạng thái 'Chờ xử lý' hoặc 'Đang xử lý'"
            )
        return data


class OrderSummarySerializer(serializers.ModelSerializer):
    """
    Serializer tóm tắt đơn hàng (dành cho list view và overview).
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    items_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_email', 'status', 'status_display',
            'total_amount', 'items_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user_email', 'status', 'status_display',
            'total_amount', 'items_count', 'created_at'
        ]
    
    def get_status_display(self, obj):
        status_choices = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý', 
            'shipped': 'Đã gửi hàng',
            'delivered': 'Đã giao hàng',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_choices.get(obj.status, obj.status)
    
    def get_items_count(self, obj):
        return obj.items.count()
