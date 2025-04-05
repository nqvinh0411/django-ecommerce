from cart.models import Cart, CartItem
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404

from core.views.base import (
    BaseAPIView, BaseListView, BaseRetrieveView, BaseUpdateView
)
from core.permissions.base import IsOwnerOrAdminUser

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


class OrderCreateView(BaseAPIView):
    """
    API để tạo đơn hàng mới từ giỏ hàng của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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
        serializer = OrderSerializer(order)
        return self.success_response(
            data=serializer.data,
            message="Đơn hàng đã được tạo thành công",
            status_code=status.HTTP_201_CREATED
        )


class UserOrderListView(BaseListView):
    """
    API để lấy danh sách đơn hàng của người dùng hiện tại.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Đơn hàng mới nhất hiển thị trước

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(BaseRetrieveView):
    """
    API để xem chi tiết một đơn hàng.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdminUser]
    lookup_url_kwarg = 'order_id'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateView(BaseUpdateView):
    """
    API để cập nhật trạng thái đơn hàng.
    - Người dùng thường chỉ có thể cập nhật trạng thái thành 'cancelled'
    - Admin/Staff có thể cập nhật bất kỳ trạng thái nào
    """
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'order_id'
    http_method_names = ['patch']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        # Kiểm tra quyền cập nhật trạng thái
        new_status = serializer.validated_data.get('status')
        instance = self.get_object()
        
        # Nếu không phải admin/staff, chỉ cho phép hủy đơn
        if not self.request.user.is_staff and new_status != 'cancelled':
            return self.error_response(
                message="Bạn chỉ có thể hủy đơn hàng của mình", 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Kiểm tra các ràng buộc khác về trạng thái
        if instance.status == 'delivered' and new_status != 'completed':
            return self.error_response(
                message="Đơn hàng đã giao không thể thay đổi trạng thái khác ngoài hoàn thành", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        if instance.status == 'cancelled':
            return self.error_response(
                message="Đơn hàng đã hủy không thể thay đổi trạng thái", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        if instance.status == 'completed':
            return self.error_response(
                message="Đơn hàng đã hoàn thành không thể thay đổi trạng thái", 
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Thực hiện cập nhật
        serializer.save()
