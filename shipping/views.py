from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import ShippingMethod, ShippingZone, ShippingRate, Shipment, TrackingInfo
from .serializers import (
    ShippingMethodSerializer, ShippingZoneSerializer, ShippingRateSerializer,
    ShipmentSerializer, ShipmentCreateSerializer, TrackingInfoSerializer, 
    TrackingInfoCreateSerializer
)
from .permissions import IsAdminUserOrReadOnly, IsOrderOwnerOrAdmin, CanManageShipment


class ShippingMethodListCreateView(generics.ListCreateAPIView):
    """
    List all shipping methods or create a new one.
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'estimated_days']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_fee', 'estimated_days', 'created_at']
    ordering = ['name']


class ShippingMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a shipping method.
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingZoneListCreateView(generics.ListCreateAPIView):
    """
    List all shipping zones or create a new one.
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'countries', 'provinces']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ShippingZoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a shipping zone.
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingRateListCreateView(generics.ListCreateAPIView):
    """
    List all shipping rates or create a new one.
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shipping_method', 'shipping_zone', 'is_active', 'currency']
    ordering_fields = ['price', 'min_weight', 'max_weight', 'created_at']
    ordering = ['shipping_method', 'shipping_zone', 'min_weight']


class ShippingRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a shipping rate.
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]


class CalculateShippingRatesView(APIView):
    """
    Calculate available shipping rates for an order.
    Requires order_id, shipping_address, and total_weight parameters.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Extract parameters
        order_id = request.data.get('order_id')
        shipping_address = request.data.get('shipping_address', {})
        total_weight = float(request.data.get('total_weight', 0))
        
        # Get country and province from address
        country = shipping_address.get('country', '')
        province = shipping_address.get('province', '')
        
        if not country or total_weight <= 0:
            return Response(
                {"detail": "Missing required parameters: country and/or total_weight"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find applicable shipping zones
        applicable_zones = []
        all_zones = ShippingZone.objects.filter(is_active=True)
        
        for zone in all_zones:
            countries_list = zone.get_countries_list()
            provinces_list = zone.get_provinces_list()
            
            # Check if this zone covers the destination
            if country in countries_list:
                # If provinces are specified, check if the province is covered
                if provinces_list and province:
                    if province in provinces_list:
                        applicable_zones.append(zone)
                else:
                    applicable_zones.append(zone)
        
        # Get available shipping rates for these zones
        available_rates = []
        
        for zone in applicable_zones:
            rates = ShippingRate.objects.filter(
                shipping_zone=zone,
                is_active=True,
                min_weight__lte=total_weight,
                max_weight__gte=total_weight
            )
            
            for rate in rates:
                # Calculate total shipping cost
                total_cost = rate.price
                if rate.shipping_method.base_fee:
                    total_cost += rate.shipping_method.base_fee
                
                available_rates.append({
                    'rate_id': rate.id,
                    'shipping_method': {
                        'id': rate.shipping_method.id,
                        'name': rate.shipping_method.name,
                        'description': rate.shipping_method.description,
                        'estimated_days': rate.shipping_method.estimated_days
                    },
                    'shipping_zone': {
                        'id': rate.shipping_zone.id,
                        'name': rate.shipping_zone.name
                    },
                    'price': rate.price,
                    'total_cost': total_cost,
                    'currency': rate.currency
                })
        
        return Response(available_rates)


class ShipmentListView(generics.ListAPIView):
    """
    List all shipments for the admin or the user's own shipments.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shipment_status', 'shipping_method']
    ordering_fields = ['created_at', 'shipped_at', 'delivered_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Shipment.objects.all()
        else:
            # Only show shipments for orders that belong to this user
            return Shipment.objects.filter(order__customer__user=user)


class ShipmentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a shipment by ID.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Shipment.objects.all()
        else:
            return Shipment.objects.filter(order__customer__user=user)


class ShipmentByOrderView(generics.RetrieveAPIView):
    """
    Retrieve a shipment for a specific order.
    """
    serializer_class = ShipmentSerializer
    permission_classes = [IsOrderOwnerOrAdmin]
    
    def get_object(self):
        order_id = self.kwargs.get('order_id')
        user = self.request.user
        
        if user.is_staff:
            return get_object_or_404(Shipment, order_id=order_id)
        else:
            return get_object_or_404(Shipment, order_id=order_id, order__customer__user=user)


class CreateShipmentView(generics.CreateAPIView):
    """
    Create a new shipment (admin only).
    """
    serializer_class = ShipmentCreateSerializer
    permission_classes = [IsAdminUser]


class AddTrackingInfoView(APIView):
    """
    Add tracking information to a shipment.
    """
    permission_classes = [CanManageShipment]
    
    def post(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        
        serializer = TrackingInfoCreateSerializer(
            data=request.data,
            context={'shipment': shipment}
        )
        
        if serializer.is_valid():
            tracking_info = serializer.save()
            
            # Update shipment status if a new status is provided
            if 'status' in request.data:
                # Map tracking status to shipment status if needed
                # This is an example mapping that can be customized
                tracking_status = request.data.get('status', '').upper()
                
                if tracking_status == 'PICKED_UP':
                    shipment.shipment_status = 'SHIPPED'
                    shipment.shipped_at = tracking_info.timestamp
                elif tracking_status == 'DELIVERED':
                    shipment.shipment_status = 'DELIVERED'
                    shipment.delivered_at = tracking_info.timestamp
                    
                shipment.save()
            
            return Response(
                TrackingInfoSerializer(tracking_info).data,
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)