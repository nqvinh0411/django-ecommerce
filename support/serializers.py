from rest_framework import serializers
from .models import SupportCategory, SupportTicket, TicketReply, FAQ
from customers.models import Customer


class SupportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportCategory
        fields = ['id', 'name', 'description']


class TicketReplySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketReply
        fields = ['id', 'message', 'is_staff_reply', 'created_at', 'user_name']
        read_only_fields = ['is_staff_reply', 'created_at', 'user_name']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def create(self, validated_data):
        # Set the user from the request
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Set is_staff_reply based on user status
        validated_data['is_staff_reply'] = user.is_staff
        
        return super().create(validated_data)


class SupportTicketSerializer(serializers.ModelSerializer):
    replies = TicketReplySerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'message', 'status', 'category', 'category_name', 
                  'created_at', 'updated_at', 'replies']
        read_only_fields = ['status', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Get customer associated with the user
            try:
                customer = Customer.objects.get(user=request.user)
                validated_data['customer'] = customer
            except Customer.DoesNotExist:
                raise serializers.ValidationError({"customer": "Customer profile not found for this user."})
        
        return super().create(validated_data)


class AdminSupportTicketSerializer(SupportTicketSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    
    class Meta(SupportTicketSerializer.Meta):
        fields = SupportTicketSerializer.Meta.fields + ['customer_name', 'customer_email']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username
    
    def get_customer_email(self, obj):
        return obj.customer.user.email


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'category_name']
