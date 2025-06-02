from products.models import Product
from products.serializers import ProductSummarySerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Review


class ReviewCreateSerializer(serializers.Serializer):
    """
    Serializer cho việc tạo đánh giá sản phẩm mới.
    """
    product_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5)
    comment = serializers.CharField(
        required=False, 
        allow_blank=True, 
        max_length=2000,
        help_text="Review comment (optional, max 2000 characters)"
    )
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            # Additional validation could be added here
            # e.g., check if product is active, available for review
        except Product.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        request = self.context.get('request')
        if request and request.user:
            # Check if user already reviewed this product
            product_id = data.get('product_id')
            if Review.objects.filter(user=request.user, product_id=product_id).exists():
                raise serializers.ValidationError(
                    "Bạn đã đánh giá sản phẩm này rồi. Vui lòng cập nhật đánh giá hiện có."
                )
        return data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc cập nhật đánh giá.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Đánh giá phải từ 1 đến 5 sao")
        return value
    
    def validate(self, data):
        """Validate if review can be updated"""
        instance = self.instance
        if instance and not instance.can_edit:
            raise serializers.ValidationError(
                "Không thể chỉnh sửa đánh giá sau 24 giờ đầu tiên"
            )
        return data


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho Review, hiển thị thông tin chi tiết của đánh giá.
    """
    user = UserSerializer(read_only=True)
    product = ProductSummarySerializer(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    rating_display = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    time_ago = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'username', 'product', 'product_name', 
            'rating', 'rating_display', 'comment', 'is_approved',
            'is_verified_purchase', 'can_edit', 'time_ago',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'username', 'product', 'product_name', 
            'is_approved', 'is_verified_purchase', 'rating_display',
            'can_edit', 'time_ago', 'created_at', 'updated_at'
        ]
    
    def get_username(self, obj):
        """Get user display name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return "Anonymous"
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    
    def get_rating_display(self, obj):
        return obj.rating_display
    
    def get_can_edit(self, obj):
        return obj.can_edit
    
    def get_time_ago(self, obj):
        """Get human-readable time since creation"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} ngày trước"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} giờ trước"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} phút trước"
        else:
            return "Vừa xong"


class ReviewSummarySerializer(serializers.ModelSerializer):
    """
    Serializer tóm tắt cho Review (dành cho list views).
    """
    username = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    rating_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'username', 'product_name', 'rating', 'rating_display',
            'comment', 'is_verified_purchase', 'created_at'
        ]
        read_only_fields = [
            'id', 'username', 'product_name', 'rating', 'rating_display',
            'comment', 'is_verified_purchase', 'created_at'
        ]
    
    def get_username(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return "Anonymous"
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    
    def get_rating_display(self, obj):
        return obj.rating_display


class ReviewModerationSerializer(serializers.ModelSerializer):
    """
    Serializer cho admin moderation của reviews.
    """
    moderated_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['is_approved', 'moderated_at', 'moderated_by', 'moderated_by_name']
        read_only_fields = ['moderated_at', 'moderated_by', 'moderated_by_name']
    
    def get_moderated_by_name(self, obj):
        if obj.moderated_by:
            return f"{obj.moderated_by.first_name} {obj.moderated_by.last_name}".strip() or obj.moderated_by.email
        return None
    
    def save(self, **kwargs):
        """Auto-set moderation fields when updating approval status"""
        from django.utils import timezone
        
        request = self.context.get('request')
        if request and request.user and 'is_approved' in self.validated_data:
            kwargs['moderated_by'] = request.user
            kwargs['moderated_at'] = timezone.now()
        
        return super().save(**kwargs)
