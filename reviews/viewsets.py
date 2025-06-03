"""
Review API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Review API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from products.models import Product
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from core.permissions import IsOwnerOrReadOnly
from core.utils.response import success_response, error_response
from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl

from .models import Review
from .serializers import (
    ReviewDetailSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ReviewSummarySerializer, ReviewModerationSerializer
)


@extend_schema(tags=['Reviews'])
class ReviewSelfViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để user quản lý Review của chính mình.
    
    Cung cấp các endpoints để user xem và quản lý đánh giá của mình.
    
    Endpoints:
    - GET /api/v1/reviews/me/ - Xem danh sách đánh giá của mình
    - POST /api/v1/reviews/me/ - Tạo đánh giá mới
    - GET /api/v1/reviews/me/{id}/ - Xem chi tiết đánh giá
    - PUT/PATCH /api/v1/reviews/me/{id}/ - Cập nhật đánh giá
    - DELETE /api/v1/reviews/me/{id}/ - Xóa đánh giá
    - GET /api/v1/reviews/me/products/{product_id}/ - Xem đánh giá cho sản phẩm cụ thể
    """
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'product', 'is_verified_purchase']
    search_fields = ['comment', 'product__name']
    ordering_fields = ['created_at', 'rating', 'updated_at']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Chỉ trả về reviews của user hiện tại."""
        if self.is_swagger_generation:
            return Review.objects.none()
        return Review.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'list':
            return ReviewSummarySerializer
        return ReviewDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Tạo đánh giá mới cho sản phẩm.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data.get('product_id')
        rating = serializer.validated_data.get('rating')
        comment = serializer.validated_data.get('comment', '')
        
        # Get product
        product = get_object_or_404(Product, id=product_id)
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        # Return created/updated review
        response_serializer = ReviewDetailSerializer(review)
        return self.success_response(
            data=response_serializer.data,
            message="Đánh giá đã được lưu thành công" if created else "Đánh giá đã được cập nhật",
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    def update(self, request, *args, **kwargs):
        """
        Cập nhật đánh giá (chỉ trong vòng 24h đầu).
        """
        review = self.get_object()
        
        if not review.can_edit:
            return self.error_response(
                message="Không thể chỉnh sửa đánh giá sau 24 giờ đầu tiên",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(review, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_serializer = ReviewDetailSerializer(review)
        return self.success_response(
            data=response_serializer.data,
            message="Đánh giá đã được cập nhật thành công",
            status_code=status.HTTP_200_OK
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update đánh giá."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='products/(?P<product_id>[^/.]+)')
    def product_review(self, request, product_id=None):
        """
        Xem đánh giá của mình cho sản phẩm cụ thể.
        """
        try:
            review = Review.objects.get(user=request.user, product_id=product_id)
            serializer = ReviewDetailSerializer(review)
            return self.success_response(
                data=serializer.data,
                message="Đánh giá của bạn cho sản phẩm này",
                status_code=status.HTTP_200_OK
            )
        except Review.DoesNotExist:
            return self.error_response(
                message="Bạn chưa đánh giá sản phẩm này",
                status_code=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Review Management'])
class ReviewAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả Review resources.
    
    Hỗ trợ tất cả các operations cho Review với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/reviews/admin/ - Liệt kê tất cả reviews (admin only)
    - GET /api/v1/reviews/admin/{id}/ - Xem chi tiết review (admin only)
    - PUT/PATCH /api/v1/reviews/admin/{id}/ - Cập nhật review (admin only)
    - DELETE /api/v1/reviews/admin/{id}/ - Xóa review (admin only)
    - PATCH /api/v1/reviews/admin/{id}/moderate/ - Moderate review
    - GET /api/v1/reviews/admin/pending/ - Reviews chờ duyệt
    """
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'product', 'user', 'is_approved', 'is_verified_purchase']
    search_fields = ['comment', 'product__name', 'user__email']
    ordering_fields = ['created_at', 'rating', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Trả về serializer phù hợp với action."""
        if self.action == 'moderate':
            return ReviewModerationSerializer
        elif self.action == 'list':
            return ReviewSummarySerializer
        return ReviewDetailSerializer
    
    @action(detail=True, methods=['patch'])
    def moderate(self, request, pk=None):
        """
        Moderate review (approve/disapprove).
        """
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_serializer = ReviewDetailSerializer(review)
        return self.success_response(
            data=response_serializer.data,
            message="Review đã được moderated thành công",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Lấy danh sách reviews chờ duyệt.
        """
        queryset = Review.objects.filter(is_approved=False)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = ReviewSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSummarySerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách reviews chờ duyệt",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Reviews'])  
class ProductReviewViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet public để xem reviews của sản phẩm.
    
    Endpoints:
    - GET /api/v1/reviews/products/{product_id}/ - Xem reviews của sản phẩm
    - GET /api/v1/reviews/products/{product_id}/stats/ - Thống kê reviews
    """
    serializer_class = ReviewSummarySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'is_verified_purchase']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    http_method_names = ['get', 'head', 'options']
    
    def get_queryset(self):
        """Trả về reviews approved của sản phẩm."""
        if self.is_swagger_generation:
            return Review.objects.none()
        
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(
            product_id=product_id,
            is_approved=True
        )
    
    def list(self, request, product_id=None, *args, **kwargs):
        """
        Lấy danh sách reviews của sản phẩm.
        """
        # Verify product exists
        get_object_or_404(Product, id=product_id)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách reviews cho sản phẩm {product_id}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request, product_id=None):
        """
        Thống kê reviews của sản phẩm.
        """
        # Verify product exists
        product = get_object_or_404(Product, id=product_id)
        
        queryset = self.get_queryset()
        
        stats = queryset.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            verified_reviews=Count('id', filter=Q(is_verified_purchase=True))
        )
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[f'rating_{i}'] = queryset.filter(rating=i).count()
        
        stats_data = {
            'product_id': product_id,
            'product_name': product.name,
            'total_reviews': stats['total_reviews'] or 0,
            'average_rating': round(stats['average_rating'] or 0, 1),
            'verified_reviews': stats['verified_reviews'] or 0,
            'rating_distribution': rating_distribution,
        }
        
        return self.success_response(
            data=stats_data,
            message="Thống kê reviews sản phẩm",
            status_code=status.HTTP_200_OK
        )
