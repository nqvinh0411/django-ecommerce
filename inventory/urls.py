from django.urls import path
from .views import (
    # Warehouse views
    WarehouseListView, WarehouseCreateView, 
    WarehouseRetrieveView, WarehouseUpdateView, WarehouseDestroyView,
    
    # StockItem views
    StockItemListView, StockItemCreateView,
    StockItemRetrieveView, StockItemUpdateView, StockItemDestroyView,
    
    # StockMovement views
    StockMovementListView, StockMovementCreateView, StockMovementRetrieveView,
    
    # InventoryAuditLog views
    InventoryAuditLogListView, InventoryAuditLogRetrieveView
)

app_name = 'inventory'

urlpatterns = [
    # Warehouse endpoints
    # GET /warehouses - liệt kê tất cả kho hàng
    path('warehouses/list', WarehouseListView.as_view(), name='warehouse-list'),
    # POST /warehouses - tạo một kho hàng mới
    path('warehouses/create', WarehouseCreateView.as_view(), name='warehouse-create'),
    # GET /warehouses/{id} - xem chi tiết một kho hàng
    path('warehouses/<int:pk>/detail', WarehouseRetrieveView.as_view(), name='warehouse-detail'),
    # PUT/PATCH /warehouses/{id} - cập nhật một kho hàng
    path('warehouses/<int:pk>/update', WarehouseUpdateView.as_view(), name='warehouse-update'),
    # DELETE /warehouses/{id} - xóa một kho hàng
    path('warehouses/<int:pk>/delete', WarehouseDestroyView.as_view(), name='warehouse-delete'),
    
    # StockItem endpoints
    # GET /stock-items - liệt kê tất cả sản phẩm trong kho
    path('stock-items/list', StockItemListView.as_view(), name='stock-item-list'),
    # POST /stock-items - tạo một sản phẩm mới trong kho
    path('stock-items/create', StockItemCreateView.as_view(), name='stock-item-create'),
    # GET /stock-items/{id} - xem chi tiết một sản phẩm trong kho
    path('stock-items/<int:pk>/detail', StockItemRetrieveView.as_view(), name='stock-item-detail'),
    # PUT/PATCH /stock-items/{id} - cập nhật một sản phẩm trong kho
    path('stock-items/<int:pk>/update', StockItemUpdateView.as_view(), name='stock-item-update'),
    # DELETE /stock-items/{id} - xóa một sản phẩm trong kho
    path('stock-items/<int:pk>/delete', StockItemDestroyView.as_view(), name='stock-item-delete'),
    
    # StockMovement endpoints
    # GET /stock-movements - liệt kê tất cả di chuyển kho
    path('stock-movements/list', StockMovementListView.as_view(), name='stock-movement-list'),
    # POST /stock-movements - tạo một di chuyển kho mới
    path('stock-movements/create', StockMovementCreateView.as_view(), name='stock-movement-create'),
    # GET /stock-movements/{id} - xem chi tiết một di chuyển kho
    path('stock-movements/<int:pk>/detail', StockMovementRetrieveView.as_view(), name='stock-movement-detail'),
    
    # InventoryAuditLog endpoints
    # GET /audit-logs - liệt kê tất cả log kiểm kê
    path('audit-logs/list', InventoryAuditLogListView.as_view(), name='inventory-audit-log-list'),
    # GET /audit-logs/{id} - xem chi tiết một log kiểm kê
    path('audit-logs/<int:pk>/detail', InventoryAuditLogRetrieveView.as_view(), name='inventory-audit-log-detail'),
]
