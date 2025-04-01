from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Tag, Attribute, AttributeValue
from .serializers import (
    CategorySerializer, BrandSerializer, TagSerializer,
    AttributeSerializer, AttributeValueSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Category management.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active', 'parent']
    search_fields = ['name', 'description']
    lookup_field = 'slug'


class BrandViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Brand management.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name', 'description']
    lookup_field = 'slug'


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Tag management.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name']
    lookup_field = 'slug'


class AttributeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Attribute management.
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_filterable', 'is_variant']
    search_fields = ['name', 'description']
    lookup_field = 'slug'


class AttributeValueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for AttributeValue management.
    """
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['attribute', 'slug']
    search_fields = ['value', 'display_value']
    
    def get_queryset(self):
        queryset = AttributeValue.objects.all()
        attribute_slug = self.request.query_params.get('attribute_slug', None)
        
        if attribute_slug:
            queryset = queryset.filter(attribute__slug=attribute_slug)
            
        return queryset