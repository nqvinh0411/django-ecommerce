from rest_framework import serializers
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity

class CustomerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerGroup
        fields = ['id', 'name', 'description', 'discount_rate', 'created_at', 'updated_at']

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'is_default', 'street_address',
            'apartment', 'city', 'state', 'postal_code', 'country',
            'phone', 'created_at', 'updated_at'
        ]

class CustomerActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerActivity
        fields = ['id', 'activity_type', 'metadata', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['created_at']

class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    addresses = CustomerAddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'phone_number', 'date_of_birth', 'gender',
            'group', 'group_name', 'loyalty_points', 'notes',
            'addresses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
