from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Warehouse, StockItem, StockMovement, InventoryAuditLog
from .serializers import (
    WarehouseSerializer, StockItemSerializer,
    StockMovementSerializer, InventoryAuditLogSerializer
)
from .permissions import IsAdminUserOrReadOnly, CreateOnlyPermission


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for warehouse management.
    Only admin users can create, update or delete warehouses.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_default', 'is_active']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'location', 'created_at']
    ordering = ['name']


class StockItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stock items management.
    Only admin users can create, update or delete stock items.
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'is_tracked', 'product']
    search_fields = ['product__name', 'warehouse__name']
    ordering_fields = ['quantity', 'last_updated', 'product__name']
    ordering = ['-last_updated']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by low stock if requested
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock == 'true':
            queryset = queryset.filter(
                quantity__lte=models.F('low_stock_threshold'),
                is_tracked=True
            )
        
        # Filter by out of stock if requested
        out_of_stock = self.request.query_params.get('out_of_stock', None)
        if out_of_stock == 'true':
            queryset = queryset.filter(quantity=0, is_tracked=True)
            
        return queryset


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stock movement operations.
    Users can only create stock movements and view them, not edit or delete.
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [CreateOnlyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'stock_item', 'stock_item__warehouse', 'created_by']
    search_fields = ['reason', 'stock_item__product__name']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by product ID if provided
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(stock_item__product_id=product_id)
            
        # Filter by warehouse ID if provided
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(stock_item__warehouse_id=warehouse_id)
            
        # Filter by order ID if provided
        order_id = self.request.query_params.get('order_id', None)
        if order_id:
            queryset = queryset.filter(related_order_id=order_id)
            
        return queryset


class InventoryAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for inventory audit logs.
    Read-only access for authenticated users. Cannot be created, modified, or deleted via API.
    """
    queryset = InventoryAuditLog.objects.all()
    serializer_class = InventoryAuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_item', 'change_type', 'stock_item__warehouse', 'changed_by']
    search_fields = ['note', 'stock_item__product__name']
    ordering_fields = ['created_at', 'old_quantity', 'new_quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by product ID if provided
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(stock_item__product_id=product_id)
            
        # Filter by warehouse ID if provided
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(stock_item__warehouse_id=warehouse_id)
            
        return queryset