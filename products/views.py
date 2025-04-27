from core.permissions.base import IsOwnerOrReadOnly, IsAdminOrReadOnly
from core.views.base import (
    BaseListCreateView, BaseRetrieveView,
    BaseUpdateView, BaseDestroyView, BaseCreateView, BaseListView
)
from core.optimization.mixins import (
    QueryOptimizationMixin, DeferUnusedFieldsMixin,
    SliceQuerySetMixin
)
from core.optimization.decorators import (
    log_slow_queries, auto_optimize_queryset
)

from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductImageSerializer


class ProductListView(QueryOptimizationMixin, SliceQuerySetMixin, BaseListView):
    queryset = Product.objects.order_by('id').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    # Tối ưu hóa queryset với các mối quan hệ
    select_related_fields = ['category']
    prefetch_related_fields = ['images']
    
    @log_slow_queries(threshold_ms=300)
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Nếu đang lọc theo category, chúng ta có thể tối ưu thêm
        category = self.request.query_params.get('category')
        if category:
            # Đã có sẵn select_related('category')
            pass
            
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


class ProductCreateView(BaseCreateView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductRetrieveView(QueryOptimizationMixin, BaseRetrieveView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    # Tối ưu hóa các trường quan hệ để tránh N+1 query
    select_related_fields = ['category']
    prefetch_related_fields = ['images']
    
    @log_slow_queries(threshold_ms=200)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductUpdateView(QueryOptimizationMixin, BaseUpdateView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    # Tối ưu hóa các trường quan hệ
    select_related_fields = ['category']

    def get_queryset(self):
        return Product.objects.all()


class ProductDestroyView(BaseDestroyView):
    queryset = Product.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()


class ProductImageUploadView(BaseCreateView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @log_slow_queries(threshold_ms=500)
    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)
