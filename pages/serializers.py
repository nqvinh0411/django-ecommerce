from rest_framework import serializers
from django.utils import timezone
from .models import Page, Banner, MenuItem


class PageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Page model.
    """
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content_html', 'content_text', 
            'is_published', 'published_at', 'seo_title', 'seo_description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_slug(self, value):
        """
        Ensure slug is unique when creating a new page or updating an existing one.
        """
        instance = self.instance
        if Page.objects.filter(slug=value).exists() and (instance is None or instance.slug != value):
            raise serializers.ValidationError("A page with this slug already exists.")
        return value


class BannerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Banner model.
    Automatically filters out expired banners.
    """
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'image', 'link_url', 'position',
            'is_active', 'start_date', 'end_date', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_expired']

    def to_representation(self, instance):
        """
        Don't return banners that have expired or are not active.
        """
        if instance.is_expired:
            # Update the is_active status if expired
            if instance.is_active:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
            
        return super().to_representation(instance)


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the MenuItem model that handles hierarchical structure.
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'label', 'url', 'order', 'parent', 
            'is_active', 'menu_type', 'children',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children(self, obj):
        """
        Get all children for this menu item.
        """
        # Only include active children
        children = obj.children.filter(is_active=True).order_by('order')
        
        if children:
            return MenuItemSerializer(children, many=True).data
        return []
    
    def to_representation(self, instance):
        """
        Customize the serialized output.
        """
        # Only include the parent_id, not the full parent object
        ret = super().to_representation(instance)
        
        # If this is not a nested serialization (i.e., child item), include the parent ID
        if 'parent' in ret and ret['parent'] is not None:
            ret['parent'] = ret['parent']
            
        return ret
