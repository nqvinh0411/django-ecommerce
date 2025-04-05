from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from core.views.base import BaseListView, BaseRetrieveView

from ..models import InventoryAuditLog
from ..serializers import InventoryAuditLogSerializer


class InventoryAuditLogListView(BaseListView):
    """
    API endpoint để liệt kê tất cả các log kiểm kê (GET).
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
        
        # Lọc theo ID sản phẩm nếu được cung cấp
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(stock_item__product_id=product_id)
            
        # Lọc theo ID kho hàng nếu được cung cấp
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(stock_item__warehouse_id=warehouse_id)
            
        return queryset


class InventoryAuditLogRetrieveView(BaseRetrieveView):
    """
    API endpoint để xem chi tiết một log kiểm kê (GET).
    """
    queryset = InventoryAuditLog.objects.all()
    serializer_class = InventoryAuditLogSerializer
    permission_classes = [IsAuthenticated]
