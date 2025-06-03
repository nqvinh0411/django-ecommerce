"""
Promotions API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Promotions API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models

from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.optimization.mixins import QueryOptimizationMixin

from .models import Coupon, PromotionCampaign, Voucher, UsageLog
from .serializers import (
    CouponSerializer, ApplyCouponSerializer,
    PromotionCampaignSerializer,
    VoucherSerializer, ApplyVoucherSerializer,
    UsageLogSerializer
)
from .permissions import CanManagePromotions


class CouponViewSet(StandardizedModelViewSet, SwaggerSchemaMixin, QueryOptimizationMixin):
    """
    ViewSet để quản lý Coupon resources.
    
    Cung cấp các operations CRUD cho mã giảm giá với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/coupons/ - Liệt kê tất cả mã giảm giá
    - POST /api/v1/promotions/coupons/ - Tạo mã giảm giá mới
    - GET /api/v1/promotions/coupons/{id}/ - Xem chi tiết mã giảm giá
    - PUT/PATCH /api/v1/promotions/coupons/{id}/ - Cập nhật mã giảm giá
    - DELETE /api/v1/promotions/coupons/{id}/ - Xóa mã giảm giá
    - POST /api/v1/promotions/coupons/apply/ - Áp dụng mã giảm giá
    """
    queryset = Coupon.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'description']
    filterset_fields = ['is_active', 'discount_type']
    ordering_fields = ['code', 'created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        if self.action == 'apply':
            return ApplyCouponSerializer
        return CouponSerializer
    
    def get_queryset(self):
        """
        Lọc mã giảm giá theo trạng thái kích hoạt và thời hạn nếu người dùng không phải admin.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return self.queryset.model.objects.none()
            
        queryset = self.queryset
        
        # Nếu không phải admin, chỉ trả về các mã giảm giá đang hoạt động
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now
            )
            queryset = queryset.filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)
            )
            queryset = queryset.filter(
                models.Q(max_uses=0) | models.Q(used_count__lt=models.F('max_uses'))
            )
            
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request):
        """
        Áp dụng mã giảm giá.
        """
        serializer = ApplyCouponSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            order_amount = serializer.validated_data['order_amount']
            
            try:
                coupon = Coupon.objects.get(code=code)
                
                if not coupon.is_valid:
                    return self.error_response(
                        message="Mã giảm giá không hợp lệ hoặc đã hết hạn",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
                if order_amount < coupon.min_order_amount:
                    return self.error_response(
                        message=f"Đơn hàng cần tối thiểu {coupon.min_order_amount} để áp dụng mã giảm giá này",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                discount_amount = coupon.calculate_discount(order_amount)
                
                return self.success_response(
                    data={
                        'coupon': CouponSerializer(coupon).data,
                        'discount_amount': discount_amount,
                        'final_amount': order_amount - discount_amount
                    },
                    message="Áp dụng mã giảm giá thành công",
                    status_code=status.HTTP_200_OK
                )
            except Coupon.DoesNotExist:
                return self.error_response(
                    message="Mã giảm giá không tồn tại",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        return self.error_response(
            errors=serializer.errors,
            message="Không thể áp dụng mã giảm giá",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PromotionCampaignViewSet(StandardizedModelViewSet, SwaggerSchemaMixin, QueryOptimizationMixin):
    """
    ViewSet để quản lý PromotionCampaign resources.
    
    Cung cấp các operations CRUD cho chiến dịch khuyến mãi với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/campaigns/ - Liệt kê tất cả chiến dịch khuyến mãi
    - POST /api/v1/promotions/campaigns/ - Tạo chiến dịch khuyến mãi mới
    - GET /api/v1/promotions/campaigns/{id}/ - Xem chi tiết chiến dịch khuyến mãi
    - PUT/PATCH /api/v1/promotions/campaigns/{id}/ - Cập nhật chiến dịch khuyến mãi
    - DELETE /api/v1/promotions/campaigns/{id}/ - Xóa chiến dịch khuyến mãi
    - GET /api/v1/promotions/campaigns/active/ - Lấy các chiến dịch đang hoạt động
    """
    queryset = PromotionCampaign.objects.all()
    permission_classes = [CanManagePromotions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active', 'products', 'categories']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    prefetch_related_fields = ['products', 'categories', 'vouchers']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        return PromotionCampaignSerializer
    
    def get_queryset(self):
        """
        Lọc chiến dịch khuyến mãi theo trạng thái kích hoạt nếu người dùng không phải admin.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return self.queryset.model.objects.none()
            
        queryset = self.queryset
        
        # Nếu không phải admin, chỉ trả về các chiến dịch đang hoạt động
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now
            )
            queryset = queryset.filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)
            )
            
        return queryset
    
    @action(detail=False, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def active(self, request):
        """
        Lấy danh sách chiến dịch đang hoạt động.
        """
        now = timezone.now()
        queryset = self.queryset.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách chiến dịch đang hoạt động",
            status_code=status.HTTP_200_OK
        )


class VoucherViewSet(StandardizedModelViewSet, SwaggerSchemaMixin, QueryOptimizationMixin):
    """
    ViewSet để quản lý Voucher resources.
    
    Cung cấp các operations CRUD cho phiếu giảm giá với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/vouchers/ - Liệt kê tất cả phiếu giảm giá
    - POST /api/v1/promotions/vouchers/ - Tạo phiếu giảm giá mới
    - GET /api/v1/promotions/vouchers/{id}/ - Xem chi tiết phiếu giảm giá
    - PUT/PATCH /api/v1/promotions/vouchers/{id}/ - Cập nhật phiếu giảm giá
    - DELETE /api/v1/promotions/vouchers/{id}/ - Xóa phiếu giảm giá
    - POST /api/v1/promotions/vouchers/apply/ - Áp dụng phiếu giảm giá
    - GET /api/v1/promotions/vouchers/my-vouchers/ - Lấy phiếu giảm giá của người dùng hiện tại
    """
    queryset = Voucher.objects.all()
    permission_classes = [CanManagePromotions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code']
    filterset_fields = ['owner', 'campaign', 'is_used']
    ordering_fields = ['created_at', 'expired_at']
    ordering = ['-created_at']
    
    select_related_fields = ['owner', 'campaign']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        if self.action == 'apply':
            return ApplyVoucherSerializer
        return VoucherSerializer
    
    def get_queryset(self):
        """
        Lọc phiếu giảm giá theo người dùng nếu không phải admin.
        """
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị phiếu giảm giá của người dùng hiện tại
        if not self.request.user.is_staff:
            try:
                customer = self.request.user.customer
                queryset = queryset.filter(owner=customer)
            except:
                return Voucher.objects.none()
            
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    @log_slow_queries(threshold_ms=500)
    def my_vouchers(self, request):
        """
        Lấy danh sách phiếu giảm giá của người dùng hiện tại.
        """
        try:
            customer = request.user.customer
            queryset = Voucher.objects.filter(owner=customer, is_used=False)
            
            # Lọc theo hạn sử dụng
            now = timezone.now()
            queryset = queryset.filter(expired_at__gt=now)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Danh sách phiếu giảm giá của bạn",
                status_code=status.HTTP_200_OK
            )
        except:
            return self.error_response(
                message="Không tìm thấy thông tin khách hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request):
        """
        Áp dụng phiếu giảm giá.
        """
        serializer = ApplyVoucherSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            order_amount = serializer.validated_data['order_amount']
            
            try:
                customer = request.user.customer
                voucher = Voucher.objects.get(code=code, owner=customer)
                
                if not voucher.is_valid:
                    return self.error_response(
                        message="Phiếu giảm giá không hợp lệ hoặc đã hết hạn",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
                if order_amount < voucher.min_order_amount:
                    return self.error_response(
                        message=f"Đơn hàng cần tối thiểu {voucher.min_order_amount} để áp dụng phiếu giảm giá này",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                discount_amount = voucher.calculate_discount(order_amount)
                
                return self.success_response(
                    data={
                        'voucher': VoucherSerializer(voucher).data,
                        'discount_amount': discount_amount,
                        'final_amount': order_amount - discount_amount
                    },
                    message="Áp dụng phiếu giảm giá thành công",
                    status_code=status.HTTP_200_OK
                )
            except Voucher.DoesNotExist:
                return self.error_response(
                    message="Phiếu giảm giá không tồn tại hoặc không thuộc về bạn",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            except:
                return self.error_response(
                    message="Không tìm thấy thông tin khách hàng",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        return self.error_response(
            errors=serializer.errors,
            message="Không thể áp dụng phiếu giảm giá",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UsageLogViewSet(StandardizedModelViewSet, SwaggerSchemaMixin, QueryOptimizationMixin):
    """
    ViewSet để quản lý UsageLog resources.
    
    Cung cấp các operations CRUD cho lịch sử sử dụng khuyến mãi với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/promotions/usage-logs/ - Liệt kê tất cả lịch sử sử dụng
    - GET /api/v1/promotions/usage-logs/{id}/ - Xem chi tiết lịch sử sử dụng
    """
    queryset = UsageLog.objects.all()
    serializer_class = UsageLogSerializer
    permission_classes = [CanManagePromotions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['promo_type', 'coupon', 'voucher', 'customer', 'order']
    search_fields = ['note']
    ordering_fields = ['used_at', 'discount_amount']
    ordering = ['-used_at']
    
    select_related_fields = ['coupon', 'voucher', 'customer', 'order']
    
    # Chỉ cho phép các thao tác đọc
    http_method_names = ['get', 'head', 'options']
    
    def get_queryset(self):
        """
        Lọc lịch sử sử dụng theo người dùng nếu không phải admin.
        """
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị lịch sử sử dụng của người dùng hiện tại
        if not self.request.user.is_staff:
            try:
                customer = self.request.user.customer
                queryset = queryset.filter(customer=customer)
            except:
                return UsageLog.objects.none()
            
        return queryset
