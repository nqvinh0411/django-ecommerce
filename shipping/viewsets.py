"""
Shipping API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Shipping API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl
from core.mixins.views import FilterByTenantMixin, PermissionByActionMixin
from core.permissions import IsAdminOrReadOnly, IsOwnerOrAdminUser

from .models import (
    ShippingMethod, ShippingZone, ShippingRate, Shipment, TrackingInfo
)
from .serializers import (
    ShippingMethodSerializer, ShippingZoneSerializer, ShippingRateSerializer,
    ShipmentSerializer, ShipmentCreateSerializer, TrackingInfoSerializer,
    TrackingInfoCreateSerializer, CalculateShippingSerializer
)


@extend_schema(tags=['Shipping'])
class ShippingMethodViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý ShippingMethod resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa phương thức vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/methods/ - Liệt kê tất cả phương thức vận chuyển
    - POST /api/v1/shipping/methods/ - Tạo phương thức vận chuyển mới (admin)
    - GET /api/v1/shipping/methods/{id}/ - Xem chi tiết phương thức vận chuyển
    - PUT/PATCH /api/v1/shipping/methods/{id}/ - Cập nhật phương thức vận chuyển (admin)
    - DELETE /api/v1/shipping/methods/{id}/ - Xóa phương thức vận chuyển (admin)
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_fee', 'estimated_days']
    ordering = ['name']
    filterset_fields = ['is_active']


@extend_schema(tags=['Shipping'])
class ShippingZoneViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý ShippingZone resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa vùng vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/zones/ - Liệt kê tất cả vùng vận chuyển
    - POST /api/v1/shipping/zones/ - Tạo vùng vận chuyển mới (admin)
    - GET /api/v1/shipping/zones/{id}/ - Xem chi tiết vùng vận chuyển
    - PUT/PATCH /api/v1/shipping/zones/{id}/ - Cập nhật vùng vận chuyển (admin)
    - DELETE /api/v1/shipping/zones/{id}/ - Xóa vùng vận chuyển (admin)
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'countries', 'provinces']
    ordering_fields = ['name']
    ordering = ['name']
    filterset_fields = ['is_active']


@extend_schema(tags=['Shipping'])
class ShippingRateViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý ShippingRate resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa biểu phí vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/rates/ - Liệt kê tất cả biểu phí vận chuyển
    - POST /api/v1/shipping/rates/ - Tạo biểu phí vận chuyển mới (admin)
    - GET /api/v1/shipping/rates/{id}/ - Xem chi tiết biểu phí vận chuyển
    - PUT/PATCH /api/v1/shipping/rates/{id}/ - Cập nhật biểu phí vận chuyển (admin)
    - DELETE /api/v1/shipping/rates/{id}/ - Xóa biểu phí vận chuyển (admin)
    - POST /api/v1/shipping/rates/calculate/ - Tính toán chi phí vận chuyển
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shipping_method', 'shipping_zone', 'is_active']
    ordering_fields = ['shipping_method', 'shipping_zone', 'min_weight', 'price']
    ordering = ['shipping_method', 'shipping_zone', 'min_weight']
    
    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        """
        Tính toán chi phí vận chuyển cho một đơn hàng dựa trên thông tin đầu vào.
        
        Args:
            request: HTTP request với địa chỉ và danh sách sản phẩm
            
        Returns:
            Response: Response với danh sách các phương thức vận chuyển khả dụng và chi phí
        """
        serializer = CalculateShippingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Giả lập tính toán chi phí vận chuyển
        country = serializer.validated_data.get('country')
        province = serializer.validated_data.get('province', '')
        weight = serializer.validated_data.get('weight', 0)
        
        # Tìm các zone phù hợp với địa chỉ
        zones = ShippingZone.objects.filter(is_active=True)
        matching_zones = []
        
        for zone in zones:
            countries = [c.strip().upper() for c in zone.countries.split(',')]
            provinces = [p.strip().upper() for p in zone.provinces.split(',') if zone.provinces]
            
            if country.upper() in countries:
                if not provinces or province.upper() in provinces:
                    matching_zones.append(zone)
        
        # Tìm các biểu phí vận chuyển phù hợp
        available_rates = []
        
        for zone in matching_zones:
            rates = ShippingRate.objects.filter(
                shipping_zone=zone,
                is_active=True,
                min_weight__lte=weight,
                max_weight__gte=weight
            )
            
            for rate in rates:
                available_rates.append({
                    'id': rate.id,
                    'shipping_method': {
                        'id': rate.shipping_method.id,
                        'name': rate.shipping_method.name,
                        'description': rate.shipping_method.description,
                        'estimated_days': rate.shipping_method.estimated_days
                    },
                    'price': float(rate.price),
                    'currency': rate.currency
                })
        
        if not available_rates:
            return self.success_response(
                data=[],
                message="Không có phương thức vận chuyển phù hợp",
                status_code=status.HTTP_200_OK
            )
        
        return self.success_response(
            data=available_rates,
            message="Danh sách phương thức vận chuyển khả dụng",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Shipping'])
class ShipmentViewSet(StandardizedModelViewSet, SwaggerSchemaMixin):
    """
    ViewSet để quản lý Shipment resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa thông tin vận chuyển đơn hàng.
    Admin có tất cả quyền, người dùng thường chỉ được xem vận chuyển của đơn hàng của họ.
    
    Endpoints:
    - GET /api/v1/shipping/shipments/ - Liệt kê tất cả đơn vận chuyển
    - POST /api/v1/shipping/shipments/ - Tạo đơn vận chuyển mới
    - GET /api/v1/shipping/shipments/{id}/ - Xem chi tiết đơn vận chuyển
    - PUT/PATCH /api/v1/shipping/shipments/{id}/ - Cập nhật đơn vận chuyển
    - DELETE /api/v1/shipping/shipments/{id}/ - Xóa đơn vận chuyển
    - GET /api/v1/shipping/shipments/order/{order_id}/ - Xem đơn vận chuyển của một đơn hàng
    - POST /api/v1/shipping/shipments/{id}/tracking/ - Thêm thông tin theo dõi vận chuyển
    """
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shipment_status', 'shipping_method']
    search_fields = ['tracking_code', 'shipping_address']
    ordering_fields = ['created_at', 'shipped_at', 'delivered_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Đảm bảo người dùng chỉ xem được đơn vận chuyển của họ,
        trừ khi là admin.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Shipment.objects.none()
            
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
        return queryset
    
    def get_permissions(self):
        """
        Thiết lập phân quyền cho từng hành động.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_tracking']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """
        Lấy thông tin vận chuyển của một đơn hàng cụ thể.
        
        Args:
            request: HTTP request
            order_id: ID của đơn hàng
            
        Returns:
            Response: Response với thông tin vận chuyển của đơn hàng
        """
        try:
            order = Order.objects.get(id=order_id)
            
            # Kiểm tra quyền truy cập
            if not request.user.is_staff and order.user != request.user:
                return self.error_response(
                    message="Bạn không có quyền xem thông tin vận chuyển của đơn hàng này",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            shipments = Shipment.objects.filter(order=order)
            serializer = self.get_serializer(shipments, many=True)
            
            return self.success_response(
                data=serializer.data,
                message=f"Thông tin vận chuyển cho đơn hàng #{order_id}",
                status_code=status.HTTP_200_OK
            )
        except Order.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy đơn hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='tracking')
    def add_tracking(self, request, pk=None):
        """
        Thêm thông tin theo dõi vận chuyển cho một đơn vận chuyển.
        
        Args:
            request: HTTP request với status, location và note
            pk: ID của đơn vận chuyển
            
        Returns:
            Response: Response với thông tin theo dõi vận chuyển đã thêm
        """
        shipment = self.get_object()
        serializer = TrackingInfoSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking_info = serializer.save(shipment=shipment)
            
            # Cập nhật trạng thái đơn vận chuyển nếu có
            if 'shipment_status' in request.data:
                shipment.shipment_status = request.data['shipment_status']
                shipment.save()
            
            return self.success_response(
                data=serializer.data,
                message="Đã thêm thông tin theo dõi vận chuyển",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Dữ liệu không hợp lệ",
            status_code=status.HTTP_400_BAD_REQUEST
        )
