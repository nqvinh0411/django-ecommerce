from rest_framework import serializers
from core.validators.common import validate_slug
from .models import Category, Brand, Tag, Attribute, AttributeValue


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value', 'display_value', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'attribute_name', 'created_at', 'updated_at']
    
    def get_attribute_name(self, obj):
        return obj.attribute.name if obj.attribute else None
    
    def validate_slug(self, value):
        return validate_slug(value)
    
    def validate(self, data):
        # Kiểm tra tính hợp lệ của các giá trị
        if 'value' in data and not data.get('value'):
            raise serializers.ValidationError({"value": "Giá trị không được để trống"})
        return data


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)
    values_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'slug', 'description', 'is_filterable', 'is_variant', 
                  'values', 'values_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'values', 'values_count', 'created_at', 'updated_at']
    
    def get_values_count(self, obj):
        return obj.values.count() if hasattr(obj, 'values') else 0
    
    def validate_slug(self, value):
        return validate_slug(value)


class RecursiveCategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CategorySerializer(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)
    parent_name = serializers.SerializerMethodField(read_only=True)
    products_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_name', 'is_active', 
                 'children', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'parent_name', 'children', 'products_count', 'created_at', 'updated_at']
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
    
    def get_products_count(self, obj):
        return obj.product_set.count() if hasattr(obj, 'product_set') else 0
    
    def validate_slug(self, value):
        return validate_slug(value)
    
    def validate(self, data):
        # Kiểm tra parent không phải là chính nó
        if data.get('parent') and data.get('parent').id == self.instance.id if self.instance else False:
            raise serializers.ValidationError({"parent": "Danh mục không thể là cha của chính nó"})
        return data


class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'is_active', 
                 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'products_count', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        return obj.product_set.count() if hasattr(obj, 'product_set') else 0
    
    def validate_slug(self, value):
        return validate_slug(value)
        

class TagSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'is_active', 'products_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'products_count', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        return obj.product_set.count() if hasattr(obj, 'product_set') else 0
    
    def validate_slug(self, value):
        return validate_slug(value)