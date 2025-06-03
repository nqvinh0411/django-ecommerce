"""
Customer API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Customer API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.viewsets.base import StandardizedModelViewSet, ReadOnlyStandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl
from core.permissions import IsAdminOrReadOnly

from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import (
    CustomerSerializer,
    CustomerDetailSerializer,
    CustomerGroupSerializer,
    CustomerAddressSerializer,
    CustomerActivitySerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer
)
from .permissions import IsCustomerOwner


@extend_schema(tags=['Customer Management'])
class CustomerViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Customer resources - dành cho admin.
    
    Hỗ trợ tất cả các operations CRUD cho Customer với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/customers/admin/ - Liệt kê tất cả khách hàng (admin only)
    - POST /api/v1/customers/admin/ - Tạo khách hàng mới (admin only)
    - GET /api/v1/customers/admin/{id}/ - Xem chi tiết khách hàng (admin only)
    - PUT/PATCH /api/v1/customers/admin/{id}/ - Cập nhật khách hàng (admin only)
    - DELETE /api/v1/customers/admin/{id}/ - Xóa khách hàng (admin only)
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'phone_number', 'user__first_name', 'user__last_name']
    filterset_fields = ['group', 'gender', 'created_at']
    ordering_fields = ['created_at', 'user__email', 'loyalty_points']
    ordering = ['-created_at']


@extend_schema(tags=['Customers'])
class CustomerSelfViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Customer profile của chính user hiện tại.
    
    Cung cấp các endpoints để user quản lý profile customer của mình.
    
    Endpoints:
    - GET /api/v1/customers/me/ - Xem profile customer của mình
    - PUT/PATCH /api/v1/customers/me/ - Cập nhật profile customer
    - POST /api/v1/customers/me/ - Tạo customer profile (nếu chưa có)
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    
    def get_queryset(self):
        """Chỉ trả về customer của user hiện tại."""
        if self.is_swagger_generation:
            return Customer.objects.none()
        return Customer.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Lấy customer object của user hiện tại."""
        try:
            return Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            return None
    
    def list(self, request, *args, **kwargs):
        """Get current user's customer profile."""
        customer = self.get_object()
        if customer:
            serializer = self.get_serializer(customer)
            return self.success_response(
                data=serializer.data,
                message="Customer profile retrieved successfully",
                status_code=status.HTTP_200_OK
            )
        return self.error_response(
            message="Customer profile not found. Please create one.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    def create(self, request, *args, **kwargs):
        """Create customer profile for current user."""
        if Customer.objects.filter(user=request.user).exists():
            return self.error_response(
                message="Customer profile already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        return self.success_response(
            data=serializer.data,
            message="Customer profile created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Update current user's customer profile."""
        customer = self.get_object()
        if not customer:
            return self.error_response(
                message="Customer profile not found. Please create one first.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return self.success_response(
            data=serializer.data,
            message="Customer profile updated successfully",
            status_code=status.HTTP_200_OK
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update current user's customer profile."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


@extend_schema(tags=['Customer Management'])
class CustomerGroupViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý CustomerGroup resources - dành cho admin.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerGroup với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/customers/groups/ - Liệt kê tất cả nhóm khách hàng
    - POST /api/v1/customers/groups/ - Tạo nhóm khách hàng mới
    - GET /api/v1/customers/groups/{id}/ - Xem chi tiết nhóm khách hàng
    - PUT/PATCH /api/v1/customers/groups/{id}/ - Cập nhật nhóm khách hàng
    - DELETE /api/v1/customers/groups/{id}/ - Xóa nhóm khách hàng
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'discount_rate', 'created_at']
    ordering = ['name']


@extend_schema(tags=['Customer Management'])
class CustomerAddressAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả CustomerAddress resources.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerAddress với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/customers/addresses/ - Liệt kê tất cả địa chỉ khách hàng (admin only)
    - POST /api/v1/customers/addresses/ - Tạo địa chỉ cho khách hàng (admin only)
    - GET /api/v1/customers/addresses/{id}/ - Xem chi tiết địa chỉ (admin only)
    - PUT/PATCH /api/v1/customers/addresses/{id}/ - Cập nhật địa chỉ (admin only)
    - DELETE /api/v1/customers/addresses/{id}/ - Xóa địa chỉ (admin only)
    """
    queryset = CustomerAddress.objects.all()
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['street_address', 'city', 'state', 'country', 'customer__user__email']
    filterset_fields = ['address_type', 'is_default', 'customer', 'customer__group']
    ordering_fields = ['created_at', 'is_default', 'customer__user__email']
    ordering = ['-created_at']


@extend_schema(tags=['Customers'])
class CustomerAddressViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý CustomerAddress của user hiện tại.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerAddress với định dạng response
    chuẩn hóa. Chỉ cho phép user quản lý địa chỉ của chính mình.
    
    Endpoints:
    - GET /api/v1/customers/me/addresses/ - Liệt kê địa chỉ của mình
    - POST /api/v1/customers/me/addresses/ - Tạo địa chỉ mới
    - GET /api/v1/customers/me/addresses/{id}/ - Xem chi tiết địa chỉ
    - PUT/PATCH /api/v1/customers/me/addresses/{id}/ - Cập nhật địa chỉ
    - DELETE /api/v1/customers/me/addresses/{id}/ - Xóa địa chỉ
    - GET /api/v1/customers/me/addresses/default_shipping/ - Lấy địa chỉ giao hàng mặc định
    - GET /api/v1/customers/me/addresses/default_billing/ - Lấy địa chỉ thanh toán mặc định
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['street_address', 'city', 'state', 'country']
    filterset_fields = ['address_type', 'is_default']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        """Lọc địa chỉ theo user hiện tại."""
        if self.is_swagger_generation:
            return CustomerAddress.objects.none()
        return CustomerAddress.objects.filter(customer__user=self.request.user)
    
    def perform_create(self, serializer):
        """Lưu customer khi tạo địa chỉ mới và cập nhật địa chỉ mặc định."""
        customer = get_object_or_404(Customer, user=self.request.user)
        # Nếu đánh dấu là địa chỉ mặc định, cập nhật các địa chỉ khác
        if serializer.validated_data.get('is_default', False):
            address_type = serializer.validated_data.get('address_type')
            if address_type in ['shipping', 'both']:
                CustomerAddress.objects.filter(
                    customer=customer,
                    address_type__in=['shipping', 'both'],
                    is_default=True
                ).update(is_default=False)
            if address_type in ['billing', 'both']:
                CustomerAddress.objects.filter(
                    customer=customer,
                    address_type__in=['billing', 'both'],
                    is_default=True
                ).update(is_default=False)
        serializer.save(customer=customer)
    
    def perform_update(self, serializer):
        """Cập nhật địa chỉ mặc định nếu cần."""
        customer = self.get_object().customer
        if serializer.validated_data.get('is_default', False):
            address_type = serializer.validated_data.get('address_type', self.get_object().address_type)
            if address_type in ['shipping', 'both']:
                CustomerAddress.objects.filter(
                    customer=customer,
                    address_type__in=['shipping', 'both'],
                    is_default=True
                ).exclude(id=self.get_object().id).update(is_default=False)
            if address_type in ['billing', 'both']:
                CustomerAddress.objects.filter(
                    customer=customer,
                    address_type__in=['billing', 'both'],
                    is_default=True
                ).exclude(id=self.get_object().id).update(is_default=False)
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def default_shipping(self, request):
        """
        Lấy địa chỉ giao hàng mặc định của khách hàng.
        
        Returns:
            Response: Response với địa chỉ giao hàng mặc định
        """
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['shipping', 'both']
        ).first()
        if address:
            serializer = self.get_serializer(address)
            return self.success_response(
                data=serializer.data,
                message="Địa chỉ giao hàng mặc định",
                status_code=status.HTTP_200_OK
            )
        return self.error_response(
            message="Không tìm thấy địa chỉ giao hàng mặc định",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def default_billing(self, request):
        """
        Lấy địa chỉ thanh toán mặc định của khách hàng.
        
        Returns:
            Response: Response với địa chỉ thanh toán mặc định
        """
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['billing', 'both']
        ).first()
        if address:
            serializer = self.get_serializer(address)
            return self.success_response(
                data=serializer.data,
                message="Địa chỉ thanh toán mặc định",
                status_code=status.HTTP_200_OK
            )
        return self.error_response(
            message="Không tìm thấy địa chỉ thanh toán mặc định",
            status_code=status.HTTP_404_NOT_FOUND
        )


@extend_schema(tags=['Customer Management'])
class CustomerActivityViewSet(SwaggerSchemaMixin, ReadOnlyStandardizedModelViewSet):
    """
    ViewSet để xem CustomerActivity resources - dành cho admin.
    
    Chỉ hỗ trợ các operations đọc (list, retrieve) cho CustomerActivity
    với định dạng response chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/customers/activities/ - Liệt kê hoạt động của khách hàng (admin only)
    - GET /api/v1/customers/activities/{id}/ - Xem chi tiết hoạt động (admin only)
    """
    queryset = CustomerActivity.objects.all()
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activity_type', 'customer__user__email']
    filterset_fields = ['activity_type', 'customer', 'created_at']
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']


@extend_schema(tags=['Customers'])
class CustomerSelfActivityViewSet(SwaggerSchemaMixin, ReadOnlyStandardizedModelViewSet):
    """
    ViewSet để user xem activity logs của chính mình.
    
    Endpoints:
    - GET /api/v1/customers/me/activities/ - Xem activity logs của mình
    - GET /api/v1/customers/me/activities/{id}/ - Xem chi tiết activity
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activity_type']
    filterset_fields = ['activity_type', 'created_at']
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Chỉ trả về activities của user hiện tại."""
        if self.is_swagger_generation:
            return CustomerActivity.objects.none()
        return CustomerActivity.objects.filter(customer__user=self.request.user)
