"""
Order API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Order API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet, ReadOnlyStandardizedModelViewSet
from core.permissions.base import IsOwnerOrAdminUser

from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


class OrderViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý Order resources.
    
    Hỗ trợ tất cả các operations CRUD cho Order với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/orders/ - Liệt kê tất cả đơn hàng của người dùng
    - POST /api/v1/orders/ - Tạo đơn hàng mới từ giỏ hàng
    - GET /api/v1/orders/{id}/ - Xem chi tiết đơn hàng
    - PUT/PATCH /api/v1/orders/{id}/ - Cập nhật đơn hàng
    - DELETE /api/v1/orders/{id}/ - Xóa đơn hàng
    - PATCH /api/v1/orders/{id}/update-status/ - Cập nhật trạng thái đơn hàng
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['id', 'status']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    lookup_url_kwarg = 'pk'
    
    def get_queryset(self):
        """
        Trả về queryset dựa trên quyền hạn của người dùng.
        Admin có thể xem tất cả đơn hàng, người dùng thường chỉ xem được đơn hàng của mình.
        """
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Tạo đơn hàng mới từ giỏ hàng của người dùng.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Response với thông tin đơn hàng đã tạo
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return self.error_response(
                message="Giỏ hàng đang trống",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Tạo đơn hàng mới
        order = Order.objects.create(user=request.user, status="pending")
        total_amount = 0
        
        # Tạo các item trong đơn hàng từ giỏ hàng
        for item in cart_items:
            item_price = item.product.price
            item_total = item_price * item.quantity
            total_amount += item_total
            
            OrderItem.objects.create(
                order=order, 
                product=item.product, 
                quantity=item.quantity,
                price=item_price
            )
        
        # Xóa giỏ hàng sau khi tạo đơn hàng
        cart_items.delete()

        # Trả về response thành công với thông tin đơn hàng
        serializer = self.get_serializer(order)
        return self.success_response(
            data=serializer.data,
            message="Đơn hàng đã được tạo thành công",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Cập nhật trạng thái đơn hàng.
        - Người dùng thường chỉ có thể cập nhật trạng thái thành 'cancelled'
        - Admin/Staff có thể cập nhật bất kỳ trạng thái nào
        
        Args:
            request: HTTP request
            pk: ID của đơn hàng
            
        Returns:
            Response: Response với thông tin đơn hàng đã cập nhật
        """
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Kiểm tra quyền cập nhật trạng thái
            new_status = serializer.validated_data.get('status')
            
            # Nếu không phải admin/staff, chỉ cho phép hủy đơn
            if not request.user.is_staff and new_status != 'cancelled':
                return self.error_response(
                    message="Bạn chỉ có thể hủy đơn hàng của mình", 
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Kiểm tra các ràng buộc khác về trạng thái
            if order.status == 'delivered' and new_status != 'completed':
                return self.error_response(
                    message="Đơn hàng đã giao không thể thay đổi trạng thái khác ngoài hoàn thành", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            if order.status == 'cancelled':
                return self.error_response(
                    message="Đơn hàng đã hủy không thể thay đổi trạng thái", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            if order.status == 'completed':
                return self.error_response(
                    message="Đơn hàng đã hoàn thành không thể thay đổi trạng thái", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Thực hiện cập nhật
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
