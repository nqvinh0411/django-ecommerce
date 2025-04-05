from django.urls import path
from .views import (
    # Warehouse views
    WarehouseListCreateView, WarehouseRetrieveUpdateDestroyView,
    # StockItem views
    StockItemListCreateView, StockItemRetrieveUpdateDestroyView,
    # StockMovement views
    StockMovementListCreateView, StockMovementRetrieveView,
    # InventoryAuditLog views
    InventoryAuditLogListView, InventoryAuditLogRetrieveView
)

app_name = 'inventory'

urlpatterns = [
    # Warehouse endpoints
    # GET /warehouses - list all warehouses
    # POST /warehouses - create a new warehouse
    path('warehouses', WarehouseListCreateView.as_view(), name='warehouse-list-create'),
    
    # GET /warehouses/{id} - retrieve a warehouse
    # PUT/PATCH /warehouses/{id} - update a warehouse
    # DELETE /warehouses/{id} - delete a warehouse
    path('warehouses/<int:pk>', WarehouseRetrieveUpdateDestroyView.as_view(), name='warehouse-detail'),
    
    # StockItem endpoints
    # GET /stock-items - list all stock items
    # POST /stock-items - create a new stock item
    path('stock-items', StockItemListCreateView.as_view(), name='stock-item-list-create'),
    
    # GET /stock-items/{id} - retrieve a stock item
    # PUT/PATCH /stock-items/{id} - update a stock item
    # DELETE /stock-items/{id} - delete a stock item
    path('stock-items/<int:pk>', StockItemRetrieveUpdateDestroyView.as_view(), name='stock-item-detail'),
    
    # StockMovement endpoints
    # GET /stock-movements - list all stock movements
    # POST /stock-movements - create a new stock movement
    path('stock-movements', StockMovementListCreateView.as_view(), name='stock-movement-list-create'),
    
    # GET /stock-movements/{id} - retrieve a stock movement
    path('stock-movements/<int:pk>', StockMovementRetrieveView.as_view(), name='stock-movement-detail'),
    
    # InventoryAuditLog endpoints
    # GET /audit-logs - list all inventory audit logs
    path('audit-logs', InventoryAuditLogListView.as_view(), name='inventory-audit-log-list'),
    
    # GET /audit-logs/{id} - retrieve an inventory audit log
    path('audit-logs/<int:pk>', InventoryAuditLogRetrieveView.as_view(), name='inventory-audit-log-detail'),
]
