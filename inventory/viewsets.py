"""
Inventory API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Inventory API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.viewsets.base import StandardizedModelViewSet
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries, cached_property_with_ttl
from core.permissions import IsAdminOrReadOnly

from .models import (
    Warehouse, StockItem, StockMovement, InventoryAuditLog
)
from .serializers import (
    WarehouseSerializer, StockItemSerializer, StockMovementSerializer, 
    InventoryAuditLogSerializer
)
from .permissions import CanManageInventory


@extend_schema(tags=['Inventory'])
class WarehouseViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Warehouse resources.
    
    Cung cấp các operations CRUD cho kho hàng với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/warehouses/ - Liệt kê tất cả kho hàng
    - POST /api/v1/inventory/warehouses/ - Tạo kho hàng mới
    - GET /api/v1/inventory/warehouses/{id}/ - Xem chi tiết kho hàng
    - PUT/PATCH /api/v1/inventory/warehouses/{id}/ - Cập nhật kho hàng
    - DELETE /api/v1/inventory/warehouses/{id}/ - Xóa kho hàng
    - GET /api/v1/inventory/warehouses/{id}/stock/ - Xem tồn kho trong kho hàng
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    filterset_fields = ['is_active', 'is_default']
    ordering_fields = ['name', 'created_at']
    ordering = ['-is_default', 'name']

    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def stock(self, request, pk=None):
        """
        Lấy danh sách tồn kho trong kho hàng.
        """
        warehouse = self.get_object()
        stock_items = warehouse.stock_items.all()
        
        # Lọc theo sản phẩm nếu có
        product_id = request.query_params.get('product_id')
        if product_id:
            stock_items = stock_items.filter(product_id=product_id)
            
        # Lọc theo trạng thái tồn kho nếu có
        is_low_stock = request.query_params.get('is_low_stock')
        if is_low_stock and is_low_stock.lower() == 'true':
            stock_items = [item for item in stock_items if item.is_low_stock]
        
        page = self.paginate_queryset(stock_items)
        
        if page is not None:
            serializer = StockItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StockItemSerializer(stock_items, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Danh sách tồn kho trong kho hàng {warehouse.name}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Inventory'])
class StockItemViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý StockItem resources.
    
    Cung cấp các operations CRUD cho tồn kho với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/stock-items/ - Liệt kê tất cả tồn kho
    - POST /api/v1/inventory/stock-items/ - Tạo tồn kho mới
    - GET /api/v1/inventory/stock-items/{id}/ - Xem chi tiết tồn kho
    - PUT/PATCH /api/v1/inventory/stock-items/{id}/ - Cập nhật tồn kho
    - DELETE /api/v1/inventory/stock-items/{id}/ - Xóa tồn kho
    - GET /api/v1/inventory/stock-items/{id}/movements/ - Xem lịch sử di chuyển
    """
    queryset = StockItem.objects.all()
    permission_classes = [CanManageInventory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse', 'is_tracked']
    search_fields = ['product__name', 'warehouse__name']
    ordering_fields = ['quantity', 'last_updated', 'product__name']
    ordering = ['product__name', 'warehouse__name']
    
    select_related_fields = ['product', 'warehouse']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        return StockItemSerializer
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def movements(self, request, pk=None):
        """
        Lấy lịch sử di chuyển của tồn kho.
        """
        stock_item = self.get_object()
        movements = stock_item.movements.all()
        
        # Lọc theo loại di chuyển nếu có
        movement_type = request.query_params.get('movement_type')
        if movement_type:
            movements = movements.filter(movement_type=movement_type)
            
        # Lọc theo khoảng thời gian nếu có
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            movements = movements.filter(created_at__gte=start_date)
        if end_date:
            movements = movements.filter(created_at__lte=end_date)
            
        page = self.paginate_queryset(movements)
        
        if page is not None:
            serializer = StockMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StockMovementSerializer(movements, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Lịch sử di chuyển của {stock_item}",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    @log_slow_queries(threshold_ms=500)
    def audit_logs(self, request, pk=None):
        """
        Lấy lịch sử kiểm kê của tồn kho.
        """
        stock_item = self.get_object()
        audit_logs = stock_item.audit_logs.all()
        
        # Lọc theo loại thay đổi nếu có
        change_type = request.query_params.get('change_type')
        if change_type:
            audit_logs = audit_logs.filter(change_type=change_type)
            
        # Lọc theo khoảng thời gian nếu có
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            audit_logs = audit_logs.filter(created_at__gte=start_date)
        if end_date:
            audit_logs = audit_logs.filter(created_at__lte=end_date)
            
        page = self.paginate_queryset(audit_logs)
        
        if page is not None:
            serializer = InventoryAuditLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = InventoryAuditLogSerializer(audit_logs, many=True)
        return self.success_response(
            data=serializer.data,
            message=f"Lịch sử kiểm kê của {stock_item}",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Inventory'])
class StockMovementViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý StockMovement resources.
    
    Cung cấp các operations CRUD cho di chuyển kho với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/stock-movements/ - Liệt kê tất cả di chuyển kho
    - POST /api/v1/inventory/stock-movements/ - Tạo di chuyển kho mới
    - GET /api/v1/inventory/stock-movements/{id}/ - Xem chi tiết di chuyển kho
    """
    queryset = StockMovement.objects.all()
    permission_classes = [CanManageInventory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_item', 'movement_type', 'related_order', 'created_by']
    search_fields = ['reason', 'stock_item__product__name']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']
    
    select_related_fields = ['stock_item', 'stock_item__product', 'stock_item__warehouse', 'created_by', 'related_order']
    
    def get_serializer_class(self):
        """
        Trả về serializer class phù hợp với hành động.
        """
        return StockMovementSerializer
    
    def perform_create(self, serializer):
        """
        Tự động thiết lập người tạo là user hiện tại.
        """
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['Inventory'])
class InventoryAuditLogViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý InventoryAuditLog resources.
    
    Cung cấp các operations đọc cho lịch sử kiểm kê với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/audit-logs/ - Liệt kê tất cả lịch sử kiểm kê
    - GET /api/v1/inventory/audit-logs/{id}/ - Xem chi tiết lịch sử kiểm kê
    """
    queryset = InventoryAuditLog.objects.all()
    serializer_class = InventoryAuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_item', 'change_type', 'changed_by']
    search_fields = ['note', 'stock_item__product__name']
    ordering_fields = ['created_at', 'old_quantity', 'new_quantity']
    ordering = ['-created_at']
    
    select_related_fields = ['stock_item', 'stock_item__product', 'stock_item__warehouse', 'changed_by']
    
    http_method_names = ['get', 'head', 'options']  # Chỉ cho phép đọc
