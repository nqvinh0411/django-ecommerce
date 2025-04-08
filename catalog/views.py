from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from core.permissions.base import IsAdminOrReadOnly

from .models import Category, Brand, Tag, Attribute, AttributeValue
from .serializers import (
    CategorySerializer, BrandSerializer, TagSerializer,
    AttributeSerializer, AttributeValueSerializer
)


# Category views
class CategoryListView(BaseListView):
    """
    API endpoint for listing all Categories (GET)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active', 'parent']
    search_fields = ['name', 'description']

class CategoryCreateView(BaseCreateView):
    """
    API endpoint for creating a new Category (POST).
    """
    pass

class CategoryRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Brand views
class BrandListCreateView(BaseListCreateView):
    """
    API endpoint for listing all Brands (GET) or creating a new Brand (POST).
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name', 'description']


class BrandRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Brand.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Tag views
class TagListCreateView(BaseListCreateView):
    """
    API endpoint for listing all Tags (GET) or creating a new Tag (POST).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name']


class TagRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Attribute views
class AttributeListCreateView(BaseListCreateView):
    """
    API endpoint for listing all Attributes (GET) or creating a new Attribute (POST).
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_filterable', 'is_variant']
    search_fields = ['name', 'description']


class AttributeRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) an Attribute.
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# AttributeValue views
class AttributeValueListCreateView(BaseListCreateView):
    """
    API endpoint for listing all AttributeValues (GET) or creating a new AttributeValue (POST).
    """
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['attribute', 'slug']
    search_fields = ['value', 'display_value']
    
    def get_queryset(self):
        queryset = AttributeValue.objects.all()
        attribute_slug = self.request.query_params.get('attribute_slug', None)
        
        if attribute_slug:
            queryset = queryset.filter(attribute__slug=attribute_slug)
            
        return queryset


class AttributeValueRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) an AttributeValue.
    """
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'