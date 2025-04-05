"""
Shipment views module
"""
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from core.views.base import BaseListView, BaseRetrieveView, BaseCreateView
from ..models import Shipment, TrackingInfo
from ..serializers import (
    ShipmentSerializer, ShipmentCreateSerializer, 
    TrackingInfoSerializer, TrackingInfoCreateSerializer
)
from ..permissions import IsOrderOwnerOrAdmin, CanManageShipment


class ShipmentListView(BaseListView):
    """
    API để liệt kê các lô hàng.
    GET /shipping/shipments
    
    Admin có thể xem tất cả lô hàng, khách hàng chỉ xem được lô hàng của họ.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shipment_status', 'shipping_method']
    ordering_fields = ['created_at', 'shipped_at', 'delivered_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return all shipments for admin or only the user's shipments for customers.
        """
        queryset = Shipment.objects.all()
        
        # Non-staff users can only see their own shipments
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
            
        return queryset


class ShipmentDetailView(BaseRetrieveView):
    """
    API để xem chi tiết một lô hàng theo ID.
    GET /shipping/shipments/{id}
    
    Admin có thể xem tất cả, khách hàng chỉ xem được lô hàng của họ.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return all shipments for admin or only the user's shipments for customers.
        """
        queryset = Shipment.objects.all()
        
        # Non-staff users can only see their own shipments
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
            
        return queryset


class ShipmentByOrderView(APIView):
    """
    API để xem thông tin lô hàng theo đơn hàng.
    GET /shipping/shipments/order/{order_id}
    
    Admin có thể xem tất cả, khách hàng chỉ xem được lô hàng của họ.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    
    def get_object(self):
        """
        Get shipment by order ID.
        """
        order_id = self.kwargs.get('order_id')
        
        shipment = get_object_or_404(Shipment, order_id=order_id)
        
        # Check permissions
        self.check_object_permissions(self.request, shipment.order)
        
        return shipment
    
    def get(self, request, order_id):
        """
        Handle GET request.
        """
        shipment = self.get_object()
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)


class CreateShipmentView(BaseCreateView):
    """
    API để tạo mới lô hàng (chỉ admin).
    POST /shipping/shipments/create
    """
    serializer_class = ShipmentCreateSerializer
    permission_classes = [IsAdminUser]


class AddTrackingInfoView(APIView):
    """
    API để thêm thông tin theo dõi cho lô hàng.
    POST /shipping/shipments/{shipment_id}/tracking
    """
    permission_classes = [CanManageShipment]
    
    def post(self, request, shipment_id):
        # Lấy thông tin lô hàng
        shipment = get_object_or_404(Shipment, id=shipment_id)
        
        # Kiểm tra quyền
        self.check_object_permissions(request, shipment)
        
        # Xác thực dữ liệu
        serializer = TrackingInfoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Cập nhật trạng thái lô hàng nếu cần
        new_status = serializer.validated_data.get('shipment_status')
        if new_status:
            shipment.shipment_status = new_status
            
            # Nếu trạng thái là "shipped", cập nhật shipped_at
            if new_status == 'shipped' and not shipment.shipped_at:
                from django.utils import timezone
                shipment.shipped_at = timezone.now()
                
            # Nếu trạng thái là "delivered", cập nhật delivered_at
            elif new_status == 'delivered' and not shipment.delivered_at:
                from django.utils import timezone
                shipment.delivered_at = timezone.now()
                
            shipment.save()
        
        # Tạo thông tin theo dõi mới
        tracking_info = serializer.save(shipment=shipment)
        
        # Trả về kết quả
        response_serializer = TrackingInfoSerializer(tracking_info)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
