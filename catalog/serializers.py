from rest_framework import serializers
from .models import Category, Brand, Tag, Attribute, AttributeValue


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'value', 'display_value', 'slug']


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'slug', 'description', 'is_filterable', 'is_variant', 'values', 'created_at', 'updated_at']


class RecursiveCategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CategorySerializer(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_name', 'is_active', 'children', 
                 'created_at', 'updated_at']
        extra_kwargs = {
            'parent': {'write_only': True}
        }
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'is_active', 'created_at', 'updated_at']
        

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'is_active', 'created_at', 'updated_at']