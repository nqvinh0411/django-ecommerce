from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView
from core.permissions.base import CreateOnlyPermission

from ..models import StockMovement, StockItem, InventoryAuditLog
from ..serializers import StockMovementSerializer


class StockMovementListView(BaseListView):
    """
    API endpoint để liệt kê tất cả di chuyển kho (GET).
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_item', 'movement_type', 'stock_item__warehouse', 'created_by']
    search_fields = ['notes', 'stock_item__product__name']
    ordering_fields = ['created_at', 'quantity_change']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lọc theo ID sản phẩm nếu được cung cấp
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(stock_item__product_id=product_id)
            
        # Lọc theo ID kho hàng nếu được cung cấp
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(stock_item__warehouse_id=warehouse_id)
            
        return queryset


class StockMovementCreateView(BaseCreateView):
    """
    API endpoint để tạo mới một di chuyển kho (POST).
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [CreateOnlyPermission]
    
    def perform_create(self, serializer):
        # Lấy thông tin từ request
        stock_item_id = serializer.validated_data.get('stock_item').id
        quantity_change = serializer.validated_data.get('quantity_change')
        
        # Lấy stock item hiện tại
        stock_item = StockItem.objects.get(id=stock_item_id)
        old_quantity = stock_item.quantity
        new_quantity = old_quantity + quantity_change
        
        # Kiểm tra xem số lượng mới có hợp lệ không (không âm)
        if new_quantity < 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"quantity_change": f"Không thể giảm số lượng quá {old_quantity} (hiện tại)."})
        
        # Cập nhật số lượng trong kho
        stock_item.quantity = new_quantity
        stock_item.save()
        
        # Lưu stock movement
        movement = serializer.save(created_by=self.request.user)
        
        # Tạo audit log
        InventoryAuditLog.objects.create(
            stock_item=stock_item,
            change_type='movement',
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            note=f"Stock movement: {movement.get_movement_type_display()} - {movement.notes}",
            changed_by=self.request.user
        )
        
        return movement


class StockMovementRetrieveView(BaseRetrieveView):
    """
    API endpoint để xem chi tiết một di chuyển kho (GET).
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
