from rest_framework import serializers
from .models import Payment
from orders.models import Order

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order', write_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'transaction_id', 'amount', 'status', 'created_at']
        read_only_fields = ['transaction_id', 'created_at']

class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'transaction_id', 'status']
