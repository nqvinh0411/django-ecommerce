"""
Product API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Product API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsOwnerOrReadOnly, IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from drf_spectacular.utils import extend_schema

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductImageSerializer


@extend_schema(tags=['Products'])
class ProductViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý Product resources.
    
    Hỗ trợ tất cả các operations CRUD cho Product với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/products/ - Liệt kê tất cả sản phẩm
    - POST /api/v1/products/ - Tạo sản phẩm mới
    - GET /api/v1/products/{id}/ - Xem chi tiết sản phẩm
    - PUT/PATCH /api/v1/products/{id}/ - Cập nhật sản phẩm
    - DELETE /api/v1/products/{id}/ - Xóa sản phẩm
    - POST /api/v1/products/{id}/upload-image/ - Tải lên hình ảnh cho sản phẩm
    """
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    # Tối ưu hóa queryset với các mối quan hệ
    select_related_fields = ['category']
    prefetch_related_fields = ['images']
    
    def get_queryset(self):
        """
        Tối ưu queryset với annotations và các mối quan hệ.
        Phân quyền khác nhau dựa vào loại request.
        """
        queryset = Product.objects.order_by('id').all()
        
        # Tính toán số lượng ảnh và đánh giá trung bình nếu có module reviews
        queryset = queryset.annotate(
            image_count=Count('images', distinct=True)
        )
        
        # Ví dụ: annotate rating nếu có app reviews
        try:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            )
        except:
            # Có thể reviews app chưa được triển khai
            pass
            
        return queryset
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Tự động thiết lập người bán là user hiện tại.
        """
        serializer.save(seller=self.request.user)
    
    @action(detail=True, methods=['post'], 
            url_path='upload-image',
            parser_classes=[MultiPartParser, FormParser],
            permission_classes=[permissions.IsAuthenticated])
    @log_slow_queries(threshold_ms=500)
    def upload_image(self, request, pk=None):
        """
        Tải lên hình ảnh cho sản phẩm.
        
        Args:
            request: HTTP request
            pk: ID của sản phẩm
            
        Returns:
            Response: Response với thông tin hình ảnh đã tải lên
        """
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            return self.success_response(
                data=serializer.data,
                message="Hình ảnh đã được tải lên thành công",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Không thể tải lên hình ảnh",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
