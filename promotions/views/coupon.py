"""
Coupon views module
"""
from django.utils import timezone
from django.db.models import Q
from django.db import models
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import Coupon, UsageLog
from ..serializers import CouponSerializer, ApplyCouponSerializer
from ..permissions import IsAdminUserOrReadOnly


class CouponListView(BaseListView):
    """
    API để liệt kê các coupon.
    GET /promotions/coupons
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    ordering_fields = ['code', 'start_date', 'end_date', 'used_count', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        Admin users can see all coupons, authenticated users only see active ones.
        """
        queryset = Coupon.objects.all()
        
        # Non-admin users only see active, valid coupons
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now
            ).filter(
                # No end_date or end_date is in the future
                Q(end_date__isnull=True) | Q(end_date__gt=now)
            ).filter(
                # No max_uses or used_count < max_uses
                Q(max_uses__isnull=True) | Q(used_count__lt=models.F('max_uses'))
            )
        
        return queryset


class CouponCreateView(BaseCreateView):
    """
    API để tạo mới coupon.
    POST /promotions/coupons
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class CouponRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một coupon.
    GET /promotions/coupons/{id}
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class CouponUpdateView(BaseUpdateView):
    """
    API để cập nhật một coupon.
    PUT/PATCH /promotions/coupons/{id}
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class CouponDestroyView(BaseDestroyView):
    """
    API để xóa một coupon.
    DELETE /promotions/coupons/{id}
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ApplyCouponView(APIView):
    """
    API để áp dụng mã giảm giá (coupon) cho đơn hàng.
    POST /promotions/coupons/apply
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        code = serializer.validated_data['code']
        order_id = serializer.validated_data['order_id']
        
        try:
            # Kiểm tra xem coupon có tồn tại và hợp lệ không
            now = timezone.now()
            coupon = Coupon.objects.get(
                code__iexact=code,
                is_active=True,
                start_date__lte=now
            )
            
            # Kiểm tra ngày hết hạn
            if coupon.end_date and coupon.end_date < now:
                return Response(
                    {"error": "Coupon has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra số lần sử dụng tối đa
            if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                return Response(
                    {"error": "Coupon has reached maximum usage limit"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra xem người dùng đã sử dụng coupon này trước đó chưa
            if coupon.once_per_customer and UsageLog.objects.filter(
                user=request.user,
                promo_id=coupon.id,
                promo_type='coupon'
            ).exists():
                return Response(
                    {"error": "You have already used this coupon before"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra xem coupon có áp dụng được cho đơn hàng không
            # Giả sử đã có Order model
            from orders.models import Order
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Kiểm tra giá trị đơn hàng tối thiểu
            if coupon.min_purchase_amount and order.total < coupon.min_purchase_amount:
                return Response(
                    {
                        "error": f"Order total must be at least {coupon.min_purchase_amount} to use this coupon"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tính toán giảm giá
            if coupon.discount_type == 'fixed':
                discount_amount = min(coupon.discount_value, order.total)
            else:  # percentage
                discount_amount = Decimal(order.total * coupon.discount_value / 100)
                if coupon.max_discount_amount:
                    discount_amount = min(discount_amount, coupon.max_discount_amount)
            
            # Cập nhật đơn hàng với giảm giá
            order.discount = discount_amount
            order.coupon = coupon
            order.save()
            
            # Ghi log sử dụng
            UsageLog.objects.create(
                user=request.user,
                promo_id=coupon.id,
                promo_type='coupon',
                order=order,
                discount_amount=discount_amount
            )
            
            # Cập nhật số lần sử dụng coupon
            coupon.used_count += 1
            coupon.save()
            
            return Response({
                "message": "Coupon applied successfully",
                "discount_amount": discount_amount,
                "new_total": order.total - discount_amount
            }, status=status.HTTP_200_OK)
            
        except Coupon.DoesNotExist:
            return Response(
                {"error": "Invalid coupon code"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
