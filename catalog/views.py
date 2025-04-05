from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    ListAPIView, CreateAPIView, RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Tag, Attribute, AttributeValue
from .serializers import (
    CategorySerializer, BrandSerializer, TagSerializer,
    AttributeSerializer, AttributeValueSerializer
)


# Category views
class CategoryListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all Categories (GET) or creating a new Category (POST).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active', 'parent']
    search_fields = ['name', 'description']


class CategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


# Brand views
class BrandListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all Brands (GET) or creating a new Brand (POST).
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name', 'description']


class BrandRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Brand.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


# Tag views
class TagListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all Tags (GET) or creating a new Tag (POST).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_active']
    search_fields = ['name']


class TagRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a Tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


# Attribute views
class AttributeListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all Attributes (GET) or creating a new Attribute (POST).
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['slug', 'is_filterable', 'is_variant']
    search_fields = ['name', 'description']


class AttributeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) an Attribute.
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


# AttributeValue views
class AttributeValueListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all AttributeValues (GET) or creating a new AttributeValue (POST).
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


class AttributeValueRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) an AttributeValue.
    """
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'