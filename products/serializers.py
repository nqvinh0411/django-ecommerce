from core.validators.common import validate_slug
from rest_framework import serializers

from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_primary', 'alt_text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        # Nếu đang đặt ảnh là primary, đảm bảo các ảnh primary khác trở thành non-primary
        if data.get('is_primary', False):
            product = data.get('product')
            if product and product.images.filter(is_primary=True).exists():
                # Chúng ta không đặt các ảnh khác thành False ở đây,
                # mà chỉ kiểm tra. Việc đặt lại sẽ được thực hiện trong save()
                pass
        return data


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    seller_username = serializers.ReadOnlyField(source='seller.username')
    primary_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name',
                  'seller_username', 'stock', 'created_at', 'updated_at',
                  'images', 'primary_image']
        read_only_fields = ['id', 'category_name', 'seller_username',
                            'created_at', 'updated_at', 'images', 'primary_image']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock']
        read_only_fields = ['id', 'updated_at', 'created_at']

    def validate_price(self, value):
        """
        Kiểm tra giá hợp lệ
        """
        if value <= 0:
            raise serializers.ValidationError("Giá phải lớn hơn 0")
        return value

    def validate_stock(self, value):
        """
        Kiểm tra số lượng tồn kho hợp lệ
        """
        if value < 0:
            raise serializers.ValidationError("Số lượng tồn kho không được âm")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['seller'] = request.user
        return super().create(validated_data)
