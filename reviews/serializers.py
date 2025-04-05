from products.models import Product
from products.serializers import ProductSerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Review


class ReviewCreateSerializer(serializers.Serializer):
    """
    Serializer cho việc tạo đánh giá sản phẩm mới.
    """
    product_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Review, hiển thị thông tin chi tiết của đánh giá.
    """
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'product', 'product_name', 
                 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'product', 'product_name', 
                           'created_at', 'updated_at']
    
    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Đánh giá phải từ 1 đến 5 sao")
        return value
