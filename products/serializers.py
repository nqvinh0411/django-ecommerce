from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    seller_username = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name',
                  'seller_id', 'seller_username', 'stock', 'created_at', 'images']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['seller'] = request.user
        return super().create(validated_data)
