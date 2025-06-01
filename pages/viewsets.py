"""
Pages API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Pages API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.optimization.mixins import QueryOptimizationMixin
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema

from .models import Page, Banner, MenuItem
from .serializers import PageSerializer, BannerSerializer, MenuItemSerializer
from .permissions import CanManagePages


@extend_schema(tags=['Pages'])
class PageViewSet(SwaggerSchemaMixin, QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Page resources.
    
    Cung cấp các operations CRUD cho trang tĩnh với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/ - Liệt kê tất cả trang tĩnh
    - POST /api/v1/pages/ - Tạo trang tĩnh mới
    - GET /api/v1/pages/{slug}/ - Xem chi tiết trang tĩnh
    - PUT/PATCH /api/v1/pages/{slug}/ - Cập nhật trang tĩnh
    - DELETE /api/v1/pages/{slug}/ - Xóa trang tĩnh
    - POST /api/v1/pages/{slug}/publish/ - Xuất bản trang tĩnh
    - POST /api/v1/pages/{slug}/unpublish/ - Hủy xuất bản trang tĩnh
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'slug'
    search_fields = ['title', 'content_text', 'seo_title', 'seo_description']
    filterset_fields = ['is_published']
    ordering_fields = ['title', 'created_at', 'published_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Lọc trang tĩnh theo trạng thái xuất bản nếu người dùng không phải admin.
        """
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị trang đã xuất bản
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
            
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[CanManagePages])
    def publish(self, request, slug=None):
        """
        Xuất bản trang tĩnh.
        """
        page = self.get_object()
        
        if page.is_published:
            return self.error_response(
                message="Trang đã được xuất bản",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        page.is_published = True
        page.published_at = timezone.now()
        page.save()
        
        serializer = self.get_serializer(page)
        return self.success_response(
            data=serializer.data,
            message="Trang đã được xuất bản thành công",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[CanManagePages])
    def unpublish(self, request, slug=None):
        """
        Hủy xuất bản trang tĩnh.
        """
        page = self.get_object()
        
        if not page.is_published:
            return self.error_response(
                message="Trang chưa được xuất bản",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        page.is_published = False
        page.save()
        
        serializer = self.get_serializer(page)
        return self.success_response(
            data=serializer.data,
            message="Đã hủy xuất bản trang",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Pages'])
class BannerViewSet(SwaggerSchemaMixin, QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Banner resources.
    
    Cung cấp các operations CRUD cho banner quảng cáo với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/banners/ - Liệt kê tất cả banner
    - POST /api/v1/pages/banners/ - Tạo banner mới
    - GET /api/v1/pages/banners/{id}/ - Xem chi tiết banner
    - PUT/PATCH /api/v1/pages/banners/{id}/ - Cập nhật banner
    - DELETE /api/v1/pages/banners/{id}/ - Xóa banner
    - GET /api/v1/pages/banners/by-position/{position}/ - Lấy banner theo vị trí
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    filterset_fields = ['position', 'is_active']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """
        Lọc banner theo trạng thái hoạt động và thời gian nếu người dùng không phải admin.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Banner.objects.none()
            
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị banner đang hoạt động và trong thời gian hiển thị
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-position/(?P<position>[^/.]+)')
    @log_slow_queries(threshold_ms=500)
    def by_position(self, request, position=None):
        """
        Lấy danh sách banner theo vị trí.
        """
        queryset = self.get_queryset().filter(position=position)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách banner ở vị trí {position}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Pages'])
class MenuItemViewSet(SwaggerSchemaMixin, QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý MenuItem resources.
    
    Cung cấp các operations CRUD cho mục menu với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/menu-items/ - Liệt kê tất cả mục menu
    - POST /api/v1/pages/menu-items/ - Tạo mục menu mới
    - GET /api/v1/pages/menu-items/{id}/ - Xem chi tiết mục menu
    - PUT/PATCH /api/v1/pages/menu-items/{id}/ - Cập nhật mục menu
    - DELETE /api/v1/pages/menu-items/{id}/ - Xóa mục menu
    - GET /api/v1/pages/menu-items/by-type/{menu_type}/ - Lấy menu theo loại
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['label', 'url']
    filterset_fields = ['menu_type', 'is_active', 'parent']
    ordering_fields = ['order', 'label', 'created_at']
    ordering = ['menu_type', 'order', 'label']
    
    select_related_fields = ['parent']
    prefetch_related_fields = ['children']
    
    def get_queryset(self):
        """
        Lọc mục menu theo trạng thái hoạt động nếu người dùng không phải admin.
        """
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị mục menu đang hoạt động
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-type/(?P<menu_type>[^/.]+)')
    @log_slow_queries(threshold_ms=500)
    def by_type(self, request, menu_type=None):
        """
        Lấy danh sách mục menu theo loại menu, chỉ trả về các mục cấp cao nhất (không có parent).
        """
        queryset = self.get_queryset().filter(menu_type=menu_type, parent__isnull=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách mục menu loại {menu_type}",
            status_code=status.HTTP_200_OK
        )
