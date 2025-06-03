from django.shortcuts import get_object_or_404
from django.db.models import Avg
from products.models import Product
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter

from core.views.base import BaseAPIView, BaseListView, BaseRetrieveUpdateDestroyView
from core.permissions import IsOwnerOrReadOnly
from core.mixins.swagger_helpers import SwaggerSchemaMixin

from .models import Review
from .serializers import ReviewDetailSerializer, ReviewCreateSerializer


class ReviewCreateView(SwaggerSchemaMixin, BaseAPIView):
    """
    API để tạo đánh giá mới cho sản phẩm.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return self.error_response(
                data=serializer.errors,
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
            
            return self.success_response(
                data=ReviewDetailSerializer(review).data,
                message="Đánh giá đã được lưu thành công",
                status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy sản phẩm",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ProductReviewListView(SwaggerSchemaMixin, BaseListView):
    """
    API để lấy danh sách đánh giá của một sản phẩm.
    """
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['comment']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)


class UserReviewListView(SwaggerSchemaMixin, BaseListView):
    """
    API để lấy danh sách đánh giá của người dùng hiện tại.
    """
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product__name', 'comment']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
            return Review.objects.none()
        return Review.objects.filter(user=self.request.user)


class ReviewDetailView(SwaggerSchemaMixin, BaseRetrieveUpdateDestroyView):
    """
    API để xem, cập nhật hoặc xóa một đánh giá cụ thể.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_url_kwarg = 'review_id'
    
    def perform_update(self, serializer):
        # Lưu đánh giá
        review = serializer.save()
        
        # Cập nhật rating trung bình cho sản phẩm
        product = review.product
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.rating = avg_rating
        product.save(update_fields=['rating'])
    
    def perform_destroy(self, instance):
        product = instance.product
        instance.delete()
        
        # Cập nhật rating trung bình cho sản phẩm sau khi xóa đánh giá
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
        product.rating = avg_rating
        product.save(update_fields=['rating'])
