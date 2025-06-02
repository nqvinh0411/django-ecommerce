from core.validators.common import validate_slug
from rest_framework import serializers
from typing import Optional, Dict, Any
from decimal import Decimal
from drf_spectacular.utils import extend_schema_field

from .models import Product, ProductImage, ProductFavorite, ProductView


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer cho ProductImage với enhanced features.
    """
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'caption', 'is_primary', 
            'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Validation logic for primary image
        product = self.context.get('product')
        if data.get('is_primary', False) and product:
            existing_primary = ProductImage.objects.filter(
                product=product, 
                is_primary=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_primary.exists():
                # Auto-handle primary image - will be handled in save()
                pass
        return data


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer cho product list views.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.SerializerMethodField(read_only=True)
    primary_image_url = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    discount_percentage = serializers.SerializerMethodField(read_only=True)
    stock_status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'compare_price',
            'category_name', 'seller_name', 'rating', 'reviews_count',
            'primary_image_url', 'is_favorited', 'discount_percentage',
            'stock_status', 'is_featured', 'created_at'
        ]
        read_only_fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'compare_price',
            'category_name', 'seller_name', 'rating', 'reviews_count',
            'primary_image_url', 'is_favorited', 'discount_percentage',
            'stock_status', 'is_featured', 'created_at'
        ]
    
    @extend_schema_field(serializers.CharField)
    def get_seller_name(self, obj):
        return f"{obj.seller.first_name} {obj.seller.last_name}".strip() or obj.seller.email
    
    @extend_schema_field(serializers.CharField)
    def get_primary_image_url(self, obj):
        primary_image = obj.primary_image
        if primary_image and primary_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProductFavorite.objects.filter(
                user=request.user, 
                product=obj
            ).exists()
        return False
    
    @extend_schema_field(serializers.DecimalField(max_digits=5, decimal_places=2))
    def get_discount_percentage(self, obj):
        return obj.discount_percentage
    
    @extend_schema_field(serializers.CharField)
    def get_stock_status(self, obj):
        if not obj.track_inventory:
            return 'available'
        elif not obj.is_in_stock:
            return 'out_of_stock'
        elif obj.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer cho product detail views.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_info = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    discount_percentage = serializers.SerializerMethodField(read_only=True)
    stock_status = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    related_products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_price', 'category', 'category_name',
            'sku', 'barcode', 'seller_info', 'status', 'is_featured',
            'is_digital', 'rating', 'reviews_count', 'views_count',
            'sales_count', 'stock', 'track_inventory', 'weight',
            'length', 'width', 'height', 'images', 'is_favorited',
            'discount_percentage', 'stock_status', 'can_edit',
            'related_products', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'sku', 'seller_info', 'rating', 'reviews_count',
            'views_count', 'sales_count', 'images', 'is_favorited',
            'discount_percentage', 'stock_status', 'can_edit', 'related_products',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_seller_info(self, obj):
        return {
            'id': obj.seller.id,
            'name': f"{obj.seller.first_name} {obj.seller.last_name}".strip() or obj.seller.email,
            'email': obj.seller.email,
        }
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProductFavorite.objects.filter(
                user=request.user, 
                product=obj
            ).exists()
        return False
    
    def get_discount_percentage(self, obj):
        return obj.discount_percentage
    
    def get_stock_status(self, obj):
        if not obj.track_inventory:
            return 'available'
        elif not obj.is_in_stock:
            return 'out_of_stock'
        elif obj.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.seller == request.user or request.user.is_staff
        return False
    
    def get_related_products(self, obj):
        # Get related products from same category (max 4)
        related = Product.objects.filter(
            category=obj.category,
            status='active'
        ).exclude(id=obj.id)[:4]
        
        return ProductSummarySerializer(
            related, 
            many=True, 
            context=self.context
        ).data


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc tạo product mới (seller).
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'price', 'compare_price',
            'category', 'stock', 'low_stock_threshold', 'track_inventory',
            'barcode', 'is_digital', 'weight', 'length', 'width', 'height',
            'meta_title', 'meta_description'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Giá phải lớn hơn 0")
        return value

    def validate_compare_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Giá so sánh phải lớn hơn 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Số lượng tồn kho không được âm")
        return value
    
    def validate(self, data):
        # Validate compare_price > price if provided
        price = data.get('price')
        compare_price = data.get('compare_price')
        
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_price': 'Giá so sánh phải lớn hơn giá bán'
            })
        
        return data


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc update product (seller).
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'price', 'compare_price',
            'category', 'stock', 'low_stock_threshold', 'track_inventory',
            'barcode', 'status', 'is_featured', 'is_digital', 'weight',
            'length', 'width', 'height', 'meta_title', 'meta_description'
        ]
    
    def validate_status(self, value):
        # Only allow certain status transitions
        instance = self.instance
        if instance:
            current_status = instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'draft': ['active', 'inactive'],
                'active': ['inactive', 'out_of_stock'],
                'inactive': ['active', 'draft'],
                'out_of_stock': ['active', 'inactive'],
                'discontinued': []  # Final state
            }
            
            if value != current_status:
                if value not in allowed_transitions.get(current_status, []):
                    raise serializers.ValidationError(
                        f"Không thể chuyển từ '{current_status}' sang '{value}'"
                    )
        
        return value
    
    def validate(self, data):
        # Same validation as create
        price = data.get('price', self.instance.price if self.instance else None)
        compare_price = data.get('compare_price')
        
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_price': 'Giá so sánh phải lớn hơn giá bán'
            })
        
        return data


class ProductFavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer cho ProductFavorite.
    """
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.filter(status='active'),
        write_only=True
    )
    
    class Meta:
        model = ProductFavorite
        fields = ['id', 'product', 'product_id', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Auto-set user from request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductImageUploadSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc upload product images.
    """
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'caption', 'is_primary', 'sort_order']
    
    def create(self, validated_data):
        # Auto-set product from context
        validated_data['product'] = self.context['product']
        return super().create(validated_data)


class ProductAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer cho product analytics (seller only).
    """
    total_revenue = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'views_count', 'sales_count', 'rating',
            'reviews_count', 'stock', 'total_revenue', 'conversion_rate',
            'created_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'name', 'views_count', 'sales_count', 'rating',
            'reviews_count', 'stock', 'total_revenue', 'conversion_rate',
            'created_at', 'published_at'
        ]
    
    def get_total_revenue(self, obj):
        return obj.sales_count * obj.price
    
    def get_conversion_rate(self, obj):
        if obj.views_count > 0:
            return round((obj.sales_count / obj.views_count) * 100, 2)
        return 0
