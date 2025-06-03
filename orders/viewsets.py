"""
Order API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Order API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from decimal import Decimal
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl
from core.permissions import IsOwnerOrAdminUser

from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderSummarySerializer,
    OrderItemSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, OrderCancelSerializer
)


@extend_schema(tags=['Order Management'])
class OrderViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả Order resources.
    
    Hỗ trợ tất cả các operations CRUD cho Order với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/orders/admin/ - Liệt kê tất cả đơn hàng (admin only)
    - POST /api/v1/orders/admin/ - Tạo đơn hàng mới (admin only)
    - GET /api/v1/orders/admin/{id}/ - Xem chi tiết đơn hàng (admin only)
    - PUT/PATCH /api/v1/orders/admin/{id}/ - Cập nhật đơn hàng (admin only)
    - DELETE /api/v1/orders/admin/{id}/ - Xóa đơn hàng (admin only)
    - PATCH /api/v1/orders/admin/{id}/update_status/ - Cập nhật trạng thái đơn hàng
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'status', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Trả về serializer class phù hợp với action."""
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        elif self.action == 'list':
            return OrderSummarySerializer
        return OrderSerializer
    
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Cập nhật trạng thái đơn hàng (Admin only).
        
        Admin có thể cập nhật bất kỳ trạng thái nào với validation logic.
        """
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Update timestamps based on status
            new_status = serializer.validated_data.get('status')
            if new_status == 'shipped' and not order.shipped_at:
                serializer.validated_data['shipped_at'] = timezone.now()
            elif new_status == 'delivered' and not order.delivered_at:
                serializer.validated_data['delivered_at'] = timezone.now()
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Cập nhật trạng thái đơn hàng thành công",
                status_code=status.HTTP_200_OK
            )
        
        return self.error_response(
            message="Dữ liệu không hợp lệ",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Orders'])
class OrderSelfViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để user quản lý Order của chính mình.
    
    Cung cấp các endpoints để user xem và quản lý đơn hàng của mình.
    
    Endpoints:
    - GET /api/v1/orders/me/ - Xem danh sách đơn hàng của mình
    - POST /api/v1/orders/me/ - Tạo đơn hàng mới từ giỏ hàng
    - GET /api/v1/orders/me/{id}/ - Xem chi tiết đơn hàng
    - PUT/PATCH /api/v1/orders/me/{id}/ - Cập nhật đơn hàng (chỉ khi pending)
    - POST /api/v1/orders/me/{id}/cancel/ - Hủy đơn hàng
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_at']
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'status', 'total_amount']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    
    def get_queryset(self):
        """Chỉ trả về đơn hàng của user hiện tại."""
        if self.is_swagger_generation:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Trả về serializer class phù hợp với action."""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'cancel':
            return OrderCancelSerializer
        elif self.action == 'list':
            return OrderSummarySerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Tạo đơn hàng mới từ giỏ hàng của user.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return self.error_response(
                message="Giỏ hàng đang trống",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate order data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Calculate totals
        subtotal = Decimal('0.00')
        for item in cart_items:
            subtotal += item.product.price * item.quantity

        # Simple calculation (có thể mở rộng thêm logic tính tax, shipping)
        tax_amount = Decimal('0.00')  # Có thể tính theo % của subtotal
        shipping_amount = Decimal('0.00')  # Có thể tính theo địa chỉ
        total_amount = subtotal + tax_amount + shipping_amount

        # Tạo đơn hàng mới
        order = Order.objects.create(
            user=request.user,
            status='pending',
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            **serializer.validated_data
        )
        
        # Tạo các order items từ cart items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                product_name=item.product.name
            )
        
        # Xóa giỏ hàng sau khi tạo đơn hàng
        cart_items.delete()

        # Trả về response với full order data
        order_serializer = OrderSerializer(order)
        return self.success_response(
            data=order_serializer.data,
            message="Đơn hàng đã được tạo thành công",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Cập nhật đơn hàng (chỉ cho phép khi status = pending).
        """
        order = self.get_object()
        
        if order.status != 'pending':
            return self.error_response(
                message="Chỉ có thể chỉnh sửa đơn hàng ở trạng thái 'Chờ xử lý'",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(order, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return self.success_response(
            data=serializer.data,
            message="Đơn hàng đã được cập nhật thành công",
            status_code=status.HTTP_200_OK
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update đơn hàng."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Hủy đơn hàng của user.
        
        User chỉ có thể hủy đơn hàng ở trạng thái pending hoặc processing.
        """
        order = self.get_object()
        
        if order.status not in ['pending', 'processing']:
            return self.error_response(
                message="Chỉ có thể hủy đơn hàng ở trạng thái 'Chờ xử lý' hoặc 'Đang xử lý'",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, context={'order': order})
        serializer.is_valid(raise_exception=True)
        
        # Cập nhật trạng thái
        order.status = 'cancelled'
        
        # Lưu lý do hủy vào notes
        reason = serializer.validated_data.get('reason', '')
        if reason:
            if order.notes:
                order.notes += f"\n\nHủy bởi user: {reason}"
            else:
                order.notes = f"Hủy bởi user: {reason}"
        
        order.save()
        
        # Trả về order đã cập nhật
        order_serializer = OrderSerializer(order)
        return self.success_response(
            data=order_serializer.data,
            message="Đơn hàng đã được hủy thành công",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Lấy lịch sử đơn hàng của user với pagination.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = OrderSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSummarySerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Lịch sử đơn hàng",
            status_code=status.HTTP_200_OK
        )
