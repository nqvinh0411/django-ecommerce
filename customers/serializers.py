from rest_framework import serializers
from typing import Optional, Dict, Any
from users.serializers import UserSerializer
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity


class CustomerGroupSerializer(serializers.ModelSerializer):
    """
    Serializer cho CustomerGroup, xử lý thông tin nhóm khách hàng.
    """
    class Meta:
        model = CustomerGroup
        fields = ['id', 'name', 'description', 'discount_rate', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_discount_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tỷ lệ giảm giá phải từ 0 đến 100%")
        return value


class CustomerAddressSerializer(serializers.ModelSerializer):
    """
    Serializer cho CustomerAddress, xử lý thông tin địa chỉ của khách hàng.
    """
    full_address = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'is_default', 'street_address',
            'apartment', 'city', 'state', 'postal_code', 'country',
            'phone', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_address(self, obj: CustomerAddress) -> str:
        parts = [obj.street_address]
        if obj.apartment:
            parts.append(obj.apartment)
        parts.extend([obj.city, obj.state, obj.postal_code, obj.country])
        return ", ".join(filter(None, parts))
    
    def validate(self, data):
        # Nếu đánh dấu là địa chỉ mặc định, thì phải cập nhật các địa chỉ khác
        if data.get('is_default', False):
            address_type = data.get('address_type')
            customer = self.context.get('customer')
            
            if not customer and self.instance:
                customer = self.instance.customer
                
            if customer and address_type:
                if address_type in ['shipping', 'both']:
                    # Logic cập nhật sẽ được xử lý trong view
                    pass
                if address_type in ['billing', 'both']:
                    # Logic cập nhật sẽ được xử lý trong view
                    pass
        
        return data


class CustomerActivitySerializer(serializers.ModelSerializer):
    """
    Serializer cho CustomerActivity, ghi lại các hoạt động của khách hàng.
    """
    customer_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CustomerActivity
        fields = ['id', 'customer', 'customer_info', 'activity_type', 'metadata', 
                 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'customer', 'customer_info', 'created_at']
    
    def get_customer_info(self, obj: CustomerActivity) -> Optional[Dict[str, Any]]:
        if obj.customer:
            return {
                "id": obj.customer.id,
                "email": obj.customer.user.email if obj.customer.user else None,
                "phone": obj.customer.phone_number
            }
        return None


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer cho Customer, xử lý thông tin khách hàng.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'user', 'username', 'email', 'phone_number', 'date_of_birth', 
            'gender', 'group', 'group_name', 'loyalty_points', 'notes',
            'addresses', 'user_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'email', 'user_details', 'created_at', 'updated_at']
    
    def validate_phone_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Số điện thoại chỉ được chứa các chữ số")
        return value
    
    def validate_loyalty_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Điểm thưởng không thể là số âm")
        return value
