"""
Voucher views module
"""
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

from core.views.base import BaseListView, BaseRetrieveView
from ..models import Voucher, UsageLog
from ..serializers import VoucherSerializer, ApplyVoucherSerializer
from ..permissions import IsOwnerOrAdmin


class CustomerVoucherListView(BaseListView):
    """
    API để liệt kê các voucher của khách hàng đã đăng nhập.
    GET /promotions/vouchers
    """
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_used']
    ordering_fields = ['created_at', 'expired_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return vouchers belonging to the authenticated customer.
        """
        now = timezone.now()
        return Voucher.objects.filter(
            customer=self.request.user,
            # Only show valid vouchers
            expired_at__gt=now
        )


class VoucherRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một voucher.
    GET /promotions/vouchers/{id}
    
    Khách hàng chỉ có thể xem voucher của chính họ.
    """
    serializer_class = VoucherSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return all vouchers for admin, or only the user's vouchers for customers.
        """
        if self.request.user.is_staff:
            return Voucher.objects.all()
        return Voucher.objects.filter(customer=self.request.user)


class ApplyVoucherView(APIView):
    """
    API để áp dụng voucher cho đơn hàng.
    POST /promotions/vouchers/apply
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyVoucherSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        voucher_id = serializer.validated_data['voucher_id']
        order_id = serializer.validated_data['order_id']
        
        try:
            # Lấy thông tin voucher
            voucher = get_object_or_404(
                Voucher, 
                id=voucher_id, 
                customer=request.user, 
                is_used=False
            )
            
            # Kiểm tra hạn sử dụng
            now = timezone.now()
            if voucher.expired_at < now:
                return Response(
                    {"error": "Voucher has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Lấy thông tin đơn hàng
            from orders.models import Order
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Kiểm tra giá trị đơn hàng tối thiểu
            if voucher.min_purchase_amount and order.total < voucher.min_purchase_amount:
                return Response(
                    {
                        "error": f"Order total must be at least {voucher.min_purchase_amount} to use this voucher"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tính toán giảm giá
            if voucher.discount_type == 'fixed':
                discount_amount = min(voucher.discount_value, order.total)
            else:  # percentage
                discount_amount = Decimal(order.total * voucher.discount_value / 100)
                if voucher.max_discount_amount:
                    discount_amount = min(discount_amount, voucher.max_discount_amount)
            
            # Cập nhật đơn hàng với giảm giá
            order.discount = discount_amount
            order.voucher = voucher
            order.save()
            
            # Ghi log sử dụng
            UsageLog.objects.create(
                user=request.user,
                promo_id=voucher.id,
                promo_type='voucher',
                order=order,
                discount_amount=discount_amount
            )
            
            # Đánh dấu voucher đã sử dụng
            voucher.is_used = True
            voucher.used_at = now
            voucher.save()
            
            return Response({
                "message": "Voucher applied successfully",
                "discount_amount": discount_amount,
                "new_total": order.total - discount_amount
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
