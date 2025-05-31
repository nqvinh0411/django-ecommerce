"""
Payment API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Payment API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

import uuid
from rest_framework import permissions, status
from rest_framework.decorators import action

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from orders.models import Order
from .models import Payment
from .serializers import PaymentStatusSerializer


class PaymentViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Payment resources.
    
    Cung cấp các endpoints để thực hiện và xem trạng thái thanh toán.
    
    Endpoints:
    - GET /api/v1/payments/ - Liệt kê các thanh toán của người dùng hiện tại
    - GET /api/v1/payments/{id}/ - Xem chi tiết thanh toán
    - POST /api/v1/payments/checkout/ - Thực hiện thanh toán
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Đảm bảo người dùng chỉ xem được các thanh toán của họ,
        trừ khi là admin.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Payment.objects.none()
            
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Thực hiện thanh toán cho một đơn hàng.
        
        Args:
            request: HTTP request với order_id
            
        Returns:
            Response: Response với thông tin thanh toán nếu thành công
        """
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if Payment.objects.filter(order=order).exists():
                return self.error_response(
                    message="Đơn hàng này đã được thanh toán",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Giả lập xử lý thanh toán (thực tế có thể tích hợp với cổng thanh toán như Stripe, VNPay)
            transaction_id = str(uuid.uuid4())  # Tạo mã giao dịch ngẫu nhiên
            payment = Payment.objects.create(
                order=order,
                transaction_id=transaction_id,
                amount=sum(item.price * item.quantity for item in order.items.all()),
                status="completed"  # Giả lập thanh toán thành công
            )

            serializer = self.get_serializer(payment)
            return self.success_response(
                data=serializer.data,
                message="Thanh toán thành công",
                status_code=status.HTTP_201_CREATED
            )
        except Order.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy đơn hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='status')
    def payment_status(self, request, pk=None):
        """
        Xem trạng thái thanh toán.
        
        Args:
            request: HTTP request
            pk: ID của thanh toán
            
        Returns:
            Response: Response với thông tin trạng thái thanh toán
        """
        payment = self.get_object()
        serializer = self.get_serializer(payment)
        
        return self.success_response(
            data=serializer.data,
            message="Thông tin trạng thái thanh toán",
            status_code=status.HTTP_200_OK
        )
