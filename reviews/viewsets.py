"""
Review API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Review API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Avg
from products.models import Product
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsOwnerOrReadOnly

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý Review resources.
    
    Hỗ trợ tất cả các operations CRUD cho Review với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/reviews/ - Liệt kê tất cả đánh giá của người dùng hiện tại
    - POST /api/v1/reviews/ - Tạo đánh giá mới cho sản phẩm
    - GET /api/v1/reviews/{id}/ - Xem chi tiết đánh giá
    - PUT/PATCH /api/v1/reviews/{id}/ - Cập nhật đánh giá
    - DELETE /api/v1/reviews/{id}/ - Xóa đánh giá
    - GET /api/v1/reviews/products/{product_id}/ - Xem đánh giá của sản phẩm
    - GET /api/v1/reviews/my-reviews/ - Xem đánh giá của người dùng hiện tại
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment', 'product__name']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Trả về queryset mặc định là đánh giá của người dùng hiện tại.
        Các actions khác sẽ override nếu cần.
        """
        if self.action == 'list':
            # Mặc định list chỉ trả về đánh giá của người dùng hiện tại
            return Review.objects.filter(user=self.request.user)
        return Review.objects.all()
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['create', 'my_reviews']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'product_reviews':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Tạo đánh giá mới cho sản phẩm.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Response với thông tin đánh giá đã tạo
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        product_id = serializer.validated_data.get('product_id')
        rating = serializer.validated_data.get('rating')
        comment = serializer.validated_data.get('comment', '')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={"rating": rating, "comment": comment}
            )
            
            # Cập nhật rating trung bình cho sản phẩm
            avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.rating = avg_rating
            product.save(update_fields=['rating'])
            
            response_serializer = ReviewSerializer(review)
            return self.success_response(
                data=response_serializer.data,
                message="Đánh giá đã được lưu thành công",
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy sản phẩm",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def perform_update(self, serializer):
        """
        Cập nhật đánh giá và cập nhật rating trung bình cho sản phẩm.
        """
        # Lưu đánh giá
        review = serializer.save()
        
        # Cập nhật rating trung bình cho sản phẩm
        product = review.product
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.rating = avg_rating
        product.save(update_fields=['rating'])
    
    def perform_destroy(self, instance):
        """
        Xóa đánh giá và cập nhật rating trung bình cho sản phẩm.
        """
        product = instance.product
        instance.delete()
        
        # Cập nhật rating trung bình cho sản phẩm sau khi xóa đánh giá
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
        product.rating = avg_rating
        product.save(update_fields=['rating'])
    
    @action(detail=False, methods=['get'], url_path='products/(?P<product_id>[^/.]+)')
    def product_reviews(self, request, product_id=None):
        """
        Lấy danh sách đánh giá của một sản phẩm.
        
        Args:
            request: HTTP request
            product_id: ID của sản phẩm
            
        Returns:
            Response: Response với danh sách đánh giá của sản phẩm
        """
        queryset = Review.objects.filter(product_id=product_id)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách đánh giá cho sản phẩm {product_id}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='my-reviews')
    def my_reviews(self, request):
        """
        Lấy danh sách đánh giá của người dùng hiện tại.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Response với danh sách đánh giá của người dùng
        """
        queryset = Review.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách đánh giá của bạn",
            status_code=status.HTTP_200_OK
        )
