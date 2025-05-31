from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from core.mixins.swagger_helpers import SwaggerSchemaMixin

from core.views.base import (
    BaseListView, BaseCreateView, BaseRetrieveView, 
    BaseUpdateView, BaseDestroyView
)

from ..models import StockItem
from ..serializers import StockItemSerializer


class StockItemListView(SwaggerSchemaMixin, BaseListView):
    """
    API endpoint để liệt kê tất cả các sản phẩm trong kho (GET).
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'product', 'status']
    search_fields = ['product__name', 'warehouse__name', 'notes']
    ordering_fields = ['quantity', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
            return StockItem.objects.none()
            
        queryset = super().get_queryset()
        
        # Lọc theo product_id nếu được cung cấp
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        # Lọc theo warehouse_id nếu được cung cấp
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
            
        return queryset


class StockItemCreateView(SwaggerSchemaMixin, BaseCreateView):
    """
    API endpoint để tạo mới một sản phẩm trong kho (POST).
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        # Logic xử lý khi tạo mới sản phẩm trong kho
        stock_item = serializer.save()
        
        # Tạo lịch sử di chuyển kho ban đầu (initial stock)
        from ..models import StockMovement, InventoryAuditLog
        
        if stock_item.quantity > 0:
            # Tạo stock movement cho việc nhập kho ban đầu
            movement = StockMovement.objects.create(
                stock_item=stock_item,
                quantity_change=stock_item.quantity,
                movement_type='initial',
                notes=f"Initial stock for {stock_item.product.name} at {stock_item.warehouse.name}",
                created_by=self.request.user
            )
            
            # Tạo audit log
            InventoryAuditLog.objects.create(
                stock_item=stock_item,
                change_type='created',
                old_quantity=0,
                new_quantity=stock_item.quantity,
                note=f"Initial stock created with quantity {stock_item.quantity}",
                changed_by=self.request.user
            )


class StockItemRetrieveView(SwaggerSchemaMixin, BaseRetrieveView):
    """
    API endpoint để xem chi tiết một sản phẩm trong kho (GET).
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]


class StockItemUpdateView(SwaggerSchemaMixin, BaseUpdateView):
    """
    API endpoint để cập nhật thông tin một sản phẩm trong kho (PUT, PATCH).
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]
    
    def perform_update(self, serializer):
        # Lấy đối tượng stock item cũ trước khi cập nhật
        stock_item = self.get_object()
        old_quantity = stock_item.quantity
        
        # Lưu stock item mới
        updated_stock_item = serializer.save()
        new_quantity = updated_stock_item.quantity
        
        # Kiểm tra nếu có sự thay đổi về số lượng
        if old_quantity != new_quantity:
            # Tạo stock movement cho việc thay đổi số lượng
            from ..models import StockMovement, InventoryAuditLog
            
            quantity_change = new_quantity - old_quantity
            movement_type = 'adjustment'
            
            # Tạo stock movement
            movement = StockMovement.objects.create(
                stock_item=updated_stock_item,
                quantity_change=quantity_change,
                movement_type=movement_type,
                notes=f"Quantity adjusted from {old_quantity} to {new_quantity}",
                created_by=self.request.user
            )
            
            # Tạo audit log
            InventoryAuditLog.objects.create(
                stock_item=updated_stock_item,
                change_type='updated',
                old_quantity=old_quantity,
                new_quantity=new_quantity,
                note=f"Quantity updated from {old_quantity} to {new_quantity}",
                changed_by=self.request.user
            )


class StockItemDestroyView(SwaggerSchemaMixin, BaseDestroyView):
    """
    API endpoint để xóa một sản phẩm trong kho (DELETE).
    """
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAdminUser]
    
    def perform_destroy(self, instance):
        # Kiểm tra nếu có stock movement liên quan
        has_movements = instance.stockmovement_set.exists()
        
        if has_movements:
            # Chuyển trạng thái thành không hoạt động thay vì xóa
            instance.status = 'inactive'
            instance.save()
            
            # Tạo audit log
            from ..models import InventoryAuditLog
            InventoryAuditLog.objects.create(
                stock_item=instance,
                change_type='deactivated',
                old_quantity=instance.quantity,
                new_quantity=instance.quantity,
                note=f"Stock item deactivated instead of deleted due to existing movements",
                changed_by=self.request.user
            )
        else:
            # Tạo audit log trước khi xóa
            from ..models import InventoryAuditLog
            InventoryAuditLog.objects.create(
                stock_item=instance,
                change_type='deleted',
                old_quantity=instance.quantity,
                new_quantity=0,
                note=f"Stock item deleted",
                changed_by=self.request.user
            )
            
            # Tiến hành xóa
            instance.delete()
