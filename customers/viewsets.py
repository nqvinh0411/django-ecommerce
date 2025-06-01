"""
Customer API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Customer API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet, ReadOnlyStandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import (
    CustomerSerializer, CustomerGroupSerializer,
    CustomerAddressSerializer, CustomerActivitySerializer
)
from .permissions import IsCustomerOwner, IsAdminOrReadOnly


@extend_schema(tags=['Customers'])
class CustomerViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Customer resources.
    
    Hỗ trợ tất cả các operations CRUD cho Customer với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customers/ - Liệt kê tất cả khách hàng
    - POST /api/v1/customers/ - Tạo khách hàng mới
    - GET /api/v1/customers/{id}/ - Xem chi tiết khách hàng
    - PUT/PATCH /api/v1/customers/{id}/ - Cập nhật khách hàng
    - DELETE /api/v1/customers/{id}/ - Xóa khách hàng
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'phone_number']
    ordering_fields = ['created_at', 'user__email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Lọc danh sách khách hàng dựa trên quyền của user."""
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Customer.objects.none()
            
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Lưu user hiện tại khi tạo khách hàng mới."""
        serializer.save(user=self.request.user)


@extend_schema(tags=['Customers'])
class CustomerGroupViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý CustomerGroup resources.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerGroup với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customer-groups/ - Liệt kê tất cả nhóm khách hàng
    - POST /api/v1/customer-groups/ - Tạo nhóm khách hàng mới
    - GET /api/v1/customer-groups/{id}/ - Xem chi tiết nhóm khách hàng
    - PUT/PATCH /api/v1/customer-groups/{id}/ - Cập nhật nhóm khách hàng
    - DELETE /api/v1/customer-groups/{id}/ - Xóa nhóm khách hàng
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'discount_rate', 'created_at']
    ordering = ['name']


@extend_schema(tags=['Customers'])
class CustomerAddressViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý CustomerAddress resources.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerAddress với định dạng response
    chuẩn hóa và phân quyền phù hợp. Cung cấp thêm các custom actions để lấy
    địa chỉ mặc định.
    
    Endpoints:
    - GET /api/v1/customer-addresses/ - Liệt kê địa chỉ của khách hàng
    - POST /api/v1/customer-addresses/ - Tạo địa chỉ mới
    - GET /api/v1/customer-addresses/{id}/ - Xem chi tiết địa chỉ
    - PUT/PATCH /api/v1/customer-addresses/{id}/ - Cập nhật địa chỉ
    - DELETE /api/v1/customer-addresses/{id}/ - Xóa địa chỉ
    - GET /api/v1/customer-addresses/default-shipping/ - Lấy địa chỉ giao hàng mặc định
    - GET /api/v1/customer-addresses/default-billing/ - Lấy địa chỉ thanh toán mặc định
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['street_address', 'city', 'state', 'country']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        """Lọc địa chỉ theo user hiện tại."""
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
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
        # Nếu đánh dấu là địa chỉ mặc định, cập nhật các địa chỉ khác
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


@extend_schema(tags=['Customers'])
class CustomerActivityViewSet(SwaggerSchemaMixin, ReadOnlyStandardizedModelViewSet):
    """
    ViewSet để xem CustomerActivity resources.
    
    Chỉ hỗ trợ các operations đọc (list, retrieve) cho CustomerActivity
    với định dạng response chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customer-activities/ - Liệt kê hoạt động của khách hàng
    - GET /api/v1/customer-activities/{id}/ - Xem chi tiết hoạt động
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activity_type', 'metadata']
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Lọc hoạt động theo user hiện tại hoặc tất cả nếu là staff."""
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation or self.swagger_fake_view:
            return CustomerActivity.objects.none()
            
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)
