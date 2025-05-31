from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from core.mixins.swagger_helpers import SwaggerSchemaMixin

from core.views.base import BaseAPIView, BaseListCreateView, BaseRetrieveUpdateDestroyView, BaseListView, BaseRetrieveView
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import (
    CustomerSerializer, CustomerGroupSerializer,
    CustomerAddressSerializer, CustomerActivitySerializer
)
from .permissions import IsCustomerOwner, IsAdminOrReadOnly


# Customer views
class CustomerListCreateView(BaseListCreateView):
    """
    API endpoint để liệt kê tất cả khách hàng hoặc tạo một khách hàng mới.
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__email', 'phone_number']
    ordering_fields = ['created_at', 'user__email']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomerRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem, cập nhật hoặc xóa thông tin khách hàng.
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    lookup_url_kwarg = 'pk'
    
    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return Customer.objects.none()
            
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)


# CustomerGroup views
class CustomerGroupListCreateView(BaseListCreateView):
    """
    API endpoint để liệt kê tất cả các nhóm khách hàng hoặc tạo một nhóm mới.
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'discount_rate', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return CustomerGroup.objects.none()
        return CustomerGroup.objects.all()


class CustomerGroupRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem, cập nhật hoặc xóa một nhóm khách hàng.
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return CustomerGroup.objects.none()
        return CustomerGroup.objects.all()


# CustomerAddress views
class CustomerAddressListCreateView(SwaggerSchemaMixin, BaseListCreateView):
    """
    API endpoint để liệt kê tất cả địa chỉ của khách hàng hoặc tạo một địa chỉ mới.
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['street_address', 'city', 'state', 'country']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']

    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return CustomerAddress.objects.none()
        return CustomerAddress.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
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


class CustomerAddressRetrieveUpdateDestroyView(SwaggerSchemaMixin, BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem, cập nhật hoặc xóa một địa chỉ của khách hàng.
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return CustomerAddress.objects.none()
        return CustomerAddress.objects.filter(customer__user=self.request.user)
        
    def perform_update(self, serializer):
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


class CustomerAddressDefaultShippingView(SwaggerSchemaMixin, BaseAPIView):
    """
    API endpoint để lấy địa chỉ giao hàng mặc định của khách hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerAddressSerializer
    
    def get(self, request):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(request, 'swagger_fake_view', False):
            return self.response(status=status.HTTP_200_OK, data={})
            
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['shipping', 'both']
        ).first()
        if address:
            serializer = CustomerAddressSerializer(address)
            return self.success_response(
                data=serializer.data,
                message="Địa chỉ giao hàng mặc định",
                status_code=status.HTTP_200_OK
            )
        return self.error_response(
            message="Không tìm thấy địa chỉ giao hàng mặc định",
            status_code=status.HTTP_404_NOT_FOUND
        )


class CustomerAddressDefaultBillingView(SwaggerSchemaMixin, BaseAPIView):
    """
    API endpoint để lấy địa chỉ thanh toán mặc định của khách hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerAddressSerializer
    
    def get(self, request):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(request, 'swagger_fake_view', False):
            return self.response(status=status.HTTP_200_OK, data={})
            
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['billing', 'both']
        ).first()
        if address:
            serializer = CustomerAddressSerializer(address)
            return self.success_response(
                data=serializer.data,
                message="Địa chỉ thanh toán mặc định",
                status_code=status.HTTP_200_OK
            )
        return self.error_response(
            message="Không tìm thấy địa chỉ thanh toán mặc định",
            status_code=status.HTTP_404_NOT_FOUND
        )


# CustomerActivity views
class CustomerActivityListView(BaseListView):
    """
    API endpoint để liệt kê tất cả hoạt động của khách hàng.
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['activity_type', 'metadata']
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']

    def get_queryset(self):
        # Xử lý trường hợp đang tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False):
            return CustomerActivity.objects.none()
            
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)


class CustomerActivityRetrieveView(BaseRetrieveView):
    """
    API endpoint để xem chi tiết một hoạt động của khách hàng.
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
            return CustomerActivity.objects.none()
            
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)