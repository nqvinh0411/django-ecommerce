"""
Catalog API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Catalog API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.optimization.mixins import QueryOptimizationMixin
from drf_spectacular.utils import extend_schema

from .models import Category, Brand, Tag, Attribute, AttributeValue
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    TagSerializer, AttributeSerializer, AttributeValueSerializer
)


@extend_schema(tags=['Catalog'])
class CategoryViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Category resources.
    
    Cung cấp các operations CRUD cho danh mục sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/categories/ - Liệt kê tất cả danh mục
    - POST /api/v1/catalog/categories/ - Tạo danh mục mới
    - GET /api/v1/catalog/categories/{slug}/ - Xem chi tiết danh mục
    - PUT/PATCH /api/v1/catalog/categories/{slug}/ - Cập nhật danh mục
    - DELETE /api/v1/catalog/categories/{slug}/ - Xóa danh mục
    - GET /api/v1/catalog/categories/{slug}/children/ - Xem danh mục con
    - GET /api/v1/catalog/categories/{slug}/descendants/ - Xem tất cả danh mục con cháu
    """
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'slug'
    search_fields = ['name', 'description']
    filterset_fields = ['is_active', 'parent']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    select_related_fields = ['parent']
    prefetch_related_fields = ['children']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        return CategorySerializer
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def children(self, request, slug=None):
        """
        Lấy danh sách danh mục con trực tiếp.
        """
        category = self.get_object()
        children = category.children.all()
        
        page = self.paginate_queryset(children)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(children, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách danh mục con của {category.name}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def descendants(self, request, slug=None):
        """
        Lấy danh sách tất cả danh mục con cháu.
        """
        category = self.get_object()
        descendants = category.get_descendants
        
        serializer = self.get_serializer(descendants, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách tất cả danh mục con cháu của {category.name}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Catalog'])
class BrandViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Brand resources.
    
    Cung cấp các operations CRUD cho thương hiệu với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/brands/ - Liệt kê tất cả thương hiệu
    - POST /api/v1/catalog/brands/ - Tạo thương hiệu mới
    - GET /api/v1/catalog/brands/{slug}/ - Xem chi tiết thương hiệu
    - PUT/PATCH /api/v1/catalog/brands/{slug}/ - Cập nhật thương hiệu
    - DELETE /api/v1/catalog/brands/{slug}/ - Xóa thương hiệu
    """
    queryset = Brand.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'slug'
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        return BrandSerializer


@extend_schema(tags=['Catalog'])
class TagViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Tag resources.
    
    Cung cấp các operations CRUD cho thẻ sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/tags/ - Liệt kê tất cả thẻ
    - POST /api/v1/catalog/tags/ - Tạo thẻ mới
    - GET /api/v1/catalog/tags/{slug}/ - Xem chi tiết thẻ
    - PUT/PATCH /api/v1/catalog/tags/{slug}/ - Cập nhật thẻ
    - DELETE /api/v1/catalog/tags/{slug}/ - Xóa thẻ
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'slug'
    search_fields = ['name']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=['Catalog'])
class AttributeViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Attribute resources.
    
    Cung cấp các operations CRUD cho thuộc tính sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/attributes/ - Liệt kê tất cả thuộc tính
    - POST /api/v1/catalog/attributes/ - Tạo thuộc tính mới
    - GET /api/v1/catalog/attributes/{slug}/ - Xem chi tiết thuộc tính
    - PUT/PATCH /api/v1/catalog/attributes/{slug}/ - Cập nhật thuộc tính
    - DELETE /api/v1/catalog/attributes/{slug}/ - Xóa thuộc tính
    - GET /api/v1/catalog/attributes/{slug}/values/ - Xem giá trị thuộc tính
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'slug'
    search_fields = ['name', 'description']
    filterset_fields = ['is_filterable', 'is_variant']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    prefetch_related_fields = ['values']
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def values(self, request, slug=None):
        """
        Lấy danh sách giá trị của thuộc tính.
        """
        attribute = self.get_object()
        values = attribute.values.all()
        
        page = self.paginate_queryset(values)
        if page is not None:
            serializer = AttributeValueSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AttributeValueSerializer(values, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách giá trị của thuộc tính {attribute.name}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Catalog'])
class AttributeValueViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý AttributeValue resources.
    
    Cung cấp các operations CRUD cho giá trị thuộc tính với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/attribute-values/ - Liệt kê tất cả giá trị thuộc tính
    - POST /api/v1/catalog/attribute-values/ - Tạo giá trị thuộc tính mới
    - GET /api/v1/catalog/attribute-values/{id}/ - Xem chi tiết giá trị thuộc tính
    - PUT/PATCH /api/v1/catalog/attribute-values/{id}/ - Cập nhật giá trị thuộc tính
    - DELETE /api/v1/catalog/attribute-values/{id}/ - Xóa giá trị thuộc tính
    """
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['value', 'display_value']
    filterset_fields = ['attribute']
    ordering_fields = ['attribute__name', 'value', 'created_at']
    ordering = ['attribute__name', 'value']
    
    select_related_fields = ['attribute']
