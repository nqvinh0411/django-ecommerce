"""
Product API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Product API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.db import models
from django.db.models import Count, Avg, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsOwnerOrReadOnly, IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema

from .models import Product, ProductImage, ProductFavorite, ProductView
from .serializers import (
    ProductDetailSerializer, ProductSummarySerializer, ProductCreateSerializer,
    ProductUpdateSerializer, ProductFavoriteSerializer, ProductImageUploadSerializer,
    ProductAnalyticsSerializer
)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@extend_schema(tags=['Products'])
class ProductPublicViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet public để xem products (không cần auth).
    
    Endpoints:
    - GET /api/v1/products/ - Xem danh sách products
    - GET /api/v1/products/{id}/ - Xem chi tiết product
    - GET /api/v1/products/featured/ - Products nổi bật
    - GET /api/v1/products/search/ - Tìm kiếm products
    """
    serializer_class = ProductSummarySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'is_featured', 'price']
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['created_at', 'price', 'rating', 'views_count', 'sales_count']
    ordering = ['-created_at']
    http_method_names = ['get', 'head', 'options']
    
    def get_queryset(self):
        """Chỉ trả về products active."""
        if self.is_swagger_generation:
            return Product.objects.none()
        
        return Product.objects.filter(
            status='active'
        ).select_related(
            'category', 'seller'
        ).prefetch_related('images')
    
    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSummarySerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Xem chi tiết product và track view.
        """
        instance = self.get_object()
        
        # Track product view
        self.track_product_view(request, instance)
        
        # Increment views count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Chi tiết sản phẩm",
            status_code=status.HTTP_200_OK
        )
    
    def track_product_view(self, request, product):
        """Track product view"""
        try:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create product view record
            ProductView.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception:
            pass  # Fail silently if view tracking fails
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Lấy danh sách products nổi bật.
        """
        queryset = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Sản phẩm nổi bật",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Lấy danh sách products trending (based on views/sales).
        """
        queryset = self.get_queryset().filter(
            views_count__gt=0
        ).order_by('-views_count', '-sales_count')[:20]
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Sản phẩm trending",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Products'])
class ProductUserViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để user quản lý Product features (favorites, recently viewed).
    
    Endpoints:
    - GET /api/v1/products/me/favorites/ - Xem favorites
    - POST /api/v1/products/me/favorites/ - Thêm favorite
    - DELETE /api/v1/products/me/favorites/{id}/ - Xóa favorite
    - GET /api/v1/products/me/recently-viewed/ - Recently viewed
    - GET /api/v1/products/me/recommendations/ - Recommendations
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Queryset depends on action."""
        if self.is_swagger_generation:
            return Product.objects.none()
        return Product.objects.filter(status='active')
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def list_favorites(self, request):
        """
        Lấy danh sách products yêu thích của user.
        """
        favorites = ProductFavorite.objects.filter(
            user=request.user
        ).select_related('product__category', 'product__seller')
        
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = ProductFavoriteSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductFavoriteSerializer(favorites, many=True, context={'request': request})
        return self.success_response(
            data=serializer.data,
            message="Danh sách sản phẩm yêu thích",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='favorites')
    def add_favorite(self, request):
        """
        Thêm product vào favorites.
        """
        serializer = ProductFavoriteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            favorite = serializer.save()
            return self.success_response(
                data=ProductFavoriteSerializer(favorite, context={'request': request}).data,
                message="Đã thêm vào danh sách yêu thích",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            if 'unique constraint' in str(e).lower():
                return self.error_response(
                    message="Sản phẩm đã có trong danh sách yêu thích",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            raise e
    
    @action(detail=True, methods=['delete'], url_path='favorites')
    def remove_favorite(self, request, pk=None):
        """
        Xóa product khỏi favorites.
        """
        try:
            favorite = ProductFavorite.objects.get(
                user=request.user,
                product_id=pk
            )
            favorite.delete()
            
            return self.success_response(
                message="Đã xóa khỏi danh sách yêu thích",
                status_code=status.HTTP_200_OK
            )
        except ProductFavorite.DoesNotExist:
            return self.error_response(
                message="Sản phẩm không có trong danh sách yêu thích",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='recently-viewed')
    def recently_viewed(self, request):
        """
        Lấy danh sách products recently viewed.
        """
        # Get recent product views (last 30 days)
        recent_views = ProductView.objects.filter(
            user=request.user,
            viewed_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).select_related('product').order_by('-viewed_at')
        
        # Get unique products (latest view first)
        seen_products = set()
        unique_views = []
        for view in recent_views:
            if view.product.id not in seen_products and view.product.status == 'active':
                unique_views.append(view)
                seen_products.add(view.product.id)
                if len(unique_views) >= 20:  # Limit to 20
                    break
        
        products = [view.product for view in unique_views]
        serializer = ProductSummarySerializer(products, many=True, context={'request': request})
        
        return self.success_response(
            data=serializer.data,
            message="Sản phẩm đã xem gần đây",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        Lấy recommendations dựa trên user behavior.
        """
        # Simple recommendation logic based on:
        # 1. Categories of favorited products
        # 2. Categories of recently viewed products
        
        # Get user's favorite categories
        favorite_categories = ProductFavorite.objects.filter(
            user=request.user
        ).values_list('product__category', flat=True).distinct()
        
        # Get recently viewed categories
        recent_categories = ProductView.objects.filter(
            user=request.user,
            viewed_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).values_list('product__category', flat=True).distinct()
        
        # Combine categories
        all_categories = set(list(favorite_categories) + list(recent_categories))
        
        if all_categories:
            # Get products from these categories
            recommendations = Product.objects.filter(
                category__in=all_categories,
                status='active'
            ).exclude(
                favorited_by__user=request.user  # Exclude already favorited
            ).order_by('-rating', '-views_count')[:10]
        else:
            # Fallback to popular products
            recommendations = Product.objects.filter(
                status='active'
            ).order_by('-rating', '-views_count')[:10]
        
        serializer = ProductSummarySerializer(recommendations, many=True, context={'request': request})
        return self.success_response(
            data=serializer.data,
            message="Gợi ý sản phẩm",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Product Management'])
class ProductSellerViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để seller quản lý Products của chính mình.
    
    Endpoints:
    - GET /api/v1/products/my-products/ - Xem products của mình
    - POST /api/v1/products/my-products/ - Tạo product mới
    - GET/PUT/PATCH /api/v1/products/my-products/{id}/ - Quản lý product
    - DELETE /api/v1/products/my-products/{id}/ - Xóa product
    - POST /api/v1/products/my-products/{id}/upload-image/ - Upload images
    - GET /api/v1/products/my-products/analytics/ - Analytics overview
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['created_at', 'price', 'stock', 'views_count', 'sales_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Chỉ trả về products của seller hiện tại."""
        if self.is_swagger_generation:
            return Product.objects.none()
        return Product.objects.filter(seller=self.request.user)
    
    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'list':
            return ProductSummarySerializer
        elif self.action == 'analytics':
            return ProductAnalyticsSerializer
        return ProductDetailSerializer
    
    def perform_create(self, serializer):
        """Auto-set seller là user hiện tại."""
        serializer.save(seller=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Cập nhật product với validation.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Special handling for status changes
        old_status = instance.status
        new_status = serializer.validated_data.get('status', old_status)
        
        if old_status != new_status and new_status == 'active':
            # Set published_at when activating
            serializer.validated_data['published_at'] = timezone.now()
        
        serializer.save()
        
        response_serializer = ProductDetailSerializer(instance, context={'request': request})
        return self.success_response(
            data=response_serializer.data,
            message="Sản phẩm đã được cập nhật thành công",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], 
            url_path='upload-image',
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """
        Upload image cho product.
        """
        product = self.get_object()
        serializer = ProductImageUploadSerializer(
            data=request.data, 
            context={'product': product, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        image = serializer.save()
        
        return self.success_response(
            data=serializer.data,
            message="Hình ảnh đã được tải lên thành công",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Analytics overview cho seller.
        """
        queryset = self.get_queryset()
        
        # Overall stats
        total_products = queryset.count()
        active_products = queryset.filter(status='active').count()
        total_views = queryset.aggregate(total=Sum('views_count'))['total'] or 0
        total_sales = queryset.aggregate(total=Sum('sales_count'))['total'] or 0
        
        # Top performing products
        top_products = queryset.filter(
            status='active'
        ).order_by('-sales_count', '-views_count')[:5]
        
        analytics_data = {
            'overview': {
                'total_products': total_products,
                'active_products': active_products,
                'total_views': total_views,
                'total_sales': total_sales,
            },
            'top_products': ProductAnalyticsSerializer(
                top_products, 
                many=True,
                context={'request': request}
            ).data
        }
        
        return self.success_response(
            data=analytics_data,
            message="Analytics overview",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def analytics_detail(self, request, pk=None):
        """
        Chi tiết analytics cho một product.
        """
        product = self.get_object()
        
        # Views over time (last 30 days)
        views_data = ProductView.objects.filter(
            product=product,
            viewed_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).extra(
            select={'date': 'date(viewed_at)'}
        ).values('date').annotate(
            views=Count('id')
        ).order_by('date')
        
        analytics_data = {
            'product': ProductAnalyticsSerializer(product, context={'request': request}).data,
            'views_over_time': list(views_data),
        }
        
        return self.success_response(
            data=analytics_data,
            message="Chi tiết analytics sản phẩm",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Product Management'])
class ProductAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả Products.
    
    Endpoints:
    - GET /api/v1/products/admin/ - Quản lý tất cả products
    - PUT/PATCH /api/v1/products/admin/{id}/ - Cập nhật product
    - DELETE /api/v1/products/admin/{id}/ - Xóa product
    - PATCH /api/v1/products/admin/{id}/feature/ - Toggle featured status
    """
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'status', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'seller__email']
    ordering_fields = ['created_at', 'price', 'views_count', 'sales_count']
    ordering = ['-created_at']
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'list':
            return ProductSummarySerializer
        return ProductDetailSerializer
    
    @action(detail=True, methods=['patch'])
    def feature(self, request, pk=None):
        """
        Toggle featured status của product.
        """
        product = self.get_object()
        is_featured = request.data.get('is_featured', not product.is_featured)
        
        product.is_featured = is_featured
        product.save(update_fields=['is_featured'])
        
        message = "Đã đánh dấu nổi bật" if is_featured else "Đã bỏ đánh dấu nổi bật"
        
        return self.success_response(
            data={'is_featured': is_featured},
            message=message,
            status_code=status.HTTP_200_OK
        )
