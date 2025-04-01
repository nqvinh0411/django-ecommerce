from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.db import models
from django.db.models import Q

from .models import Coupon, PromotionCampaign, Voucher, UsageLog
from .serializers import (
    CouponSerializer, PromotionCampaignSerializer, VoucherSerializer,
    UsageLogSerializer, ApplyCouponSerializer, ApplyVoucherSerializer
)
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrAdmin


class CouponListCreateView(generics.ListCreateAPIView):
    """
    List all coupons or create a new one.
    Admin only for creation, admin and authenticated users for viewing.
    """
    queryset = Coupon.objects.all()
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
        queryset = super().get_queryset()
        
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
                Q(max_uses=0) | Q(used_count__lt=models.F('max_uses'))
            )
            
        return queryset


class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a coupon.
    Admin only for update/delete, admin and authenticated users for viewing.
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class PromotionCampaignListView(generics.ListAPIView):
    """
    List all active promotion campaigns.
    Public endpoint with read-only access.
    """
    serializer_class = PromotionCampaignSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """
        Filter campaigns to show only active ones with valid dates.
        """
        now = timezone.now()
        return PromotionCampaign.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            # No end_date or end_date is in the future
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        )


class PromotionCampaignAdminListCreateView(generics.ListCreateAPIView):
    """
    List all promotion campaigns or create a new one.
    Admin only endpoint.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']


class PromotionCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a promotion campaign.
    Admin only endpoint.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]


class CustomerVoucherListView(generics.ListAPIView):
    """
    List all vouchers for the currently authenticated customer.
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
        if hasattr(self.request.user, 'customer'):
            return Voucher.objects.filter(owner=self.request.user.customer)
        return Voucher.objects.none()


class VoucherDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific voucher.
    Customers can only view their own vouchers.
    """
    serializer_class = VoucherSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return all vouchers for admin, or only the user's vouchers for customers.
        """
        if self.request.user.is_staff:
            return Voucher.objects.all()
        
        if hasattr(self.request.user, 'customer'):
            return Voucher.objects.filter(owner=self.request.user.customer)
            
        return Voucher.objects.none()


class ApplyCouponView(APIView):
    """
    Apply a coupon code to an order.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            order_id = serializer.validated_data['order_id']
            
            # Import Order model
            from django.apps import apps
            Order = apps.get_model('orders', 'Order')
            order = get_object_or_404(Order, id=order_id)
            
            # Check if the user is authorized to apply coupon to this order
            if not request.user.is_staff and (not hasattr(order, 'customer') or 
                                             order.customer.user != request.user):
                return Response(
                    {"detail": "You are not authorized to apply coupons to this order."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Try to find coupon first
            try:
                coupon = Coupon.objects.get(code=code)
                if not coupon.is_valid:
                    return Response(
                        {"detail": "This coupon is no longer valid."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                # Check minimum order amount
                if order.total < coupon.min_order_amount:
                    return Response(
                        {"detail": f"Order total must be at least {coupon.min_order_amount} to use this coupon."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate discount
                discount_amount = Decimal(coupon.calculate_discount(float(order.total)))
                
                # Create usage log
                usage_log = UsageLog.objects.create(
                    promo_type='coupon',
                    coupon=coupon,
                    customer=order.customer,
                    order=order,
                    discount_amount=discount_amount,
                    note=f"Applied coupon {code} to order #{order.id}"
                )
                
                # Update order with discount
                order.discount = discount_amount
                order.save()
                
                return Response({
                    "detail": "Coupon applied successfully.",
                    "discount_amount": discount_amount,
                    "new_total": order.total - discount_amount
                })
                
            except Coupon.DoesNotExist:
                # Not a coupon, so return an error
                return Response(
                    {"detail": "Invalid coupon code."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplyVoucherView(APIView):
    """
    Apply a voucher to an order.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ApplyVoucherSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            code = serializer.validated_data['code']
            order_id = serializer.validated_data['order_id']
            
            # Import Order model
            from django.apps import apps
            Order = apps.get_model('orders', 'Order')
            order = get_object_or_404(Order, id=order_id)
            
            # Check if the user is authorized to apply voucher to this order
            if not hasattr(order, 'customer') or order.customer.user != request.user:
                return Response(
                    {"detail": "You can only apply vouchers to your own orders."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get the voucher
            try:
                voucher = Voucher.objects.get(code=code, owner=request.user.customer)
                if not voucher.is_valid:
                    return Response(
                        {"detail": "This voucher is no longer valid."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                # Check minimum order amount
                if order.total < voucher.min_order_amount:
                    return Response(
                        {"detail": f"Order total must be at least {voucher.min_order_amount} to use this voucher."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate discount
                discount_amount = Decimal(voucher.calculate_discount(float(order.total)))
                
                # Create usage log
                usage_log = UsageLog.objects.create(
                    promo_type='voucher',
                    voucher=voucher,
                    customer=order.customer,
                    order=order,
                    discount_amount=discount_amount,
                    note=f"Applied voucher {code} to order #{order.id}"
                )
                
                # Update order with discount
                order.discount = discount_amount
                order.save()
                
                return Response({
                    "detail": "Voucher applied successfully.",
                    "discount_amount": discount_amount,
                    "new_total": order.total - discount_amount
                })
                
            except Voucher.DoesNotExist:
                return Response(
                    {"detail": "Invalid voucher code or this voucher does not belong to you."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsageLogListView(generics.ListAPIView):
    """
    List usage logs for promotions.
    Admin can see all logs, customers can only see their own.
    """
    serializer_class = UsageLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['promo_type']
    ordering_fields = ['used_at']
    ordering = ['-used_at']
    
    def get_queryset(self):
        """
        Return all logs for admin, or only the user's logs for customers.
        """
        if self.request.user.is_staff:
            return UsageLog.objects.all()
        
        if hasattr(self.request.user, 'customer'):
            return UsageLog.objects.filter(customer=self.request.user.customer)
            
        return UsageLog.objects.none()
