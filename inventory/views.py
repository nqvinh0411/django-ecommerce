"""
Inventory views module - exports all view classes for the inventory app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
from .views.warehouse import (
    WarehouseListView, WarehouseCreateView, 
    WarehouseRetrieveView, WarehouseUpdateView, WarehouseDestroyView
)
from .views.stock_item import (
    StockItemListView, StockItemCreateView,
    StockItemRetrieveView, StockItemUpdateView, StockItemDestroyView
)
from .views.stock_movement import (
    StockMovementListView, StockMovementCreateView, StockMovementRetrieveView
)
from .views.audit_log import (
    InventoryAuditLogListView, InventoryAuditLogRetrieveView
)

__all__ = [
    # Warehouse views
    'WarehouseListView', 'WarehouseCreateView', 
    'WarehouseRetrieveView', 'WarehouseUpdateView', 'WarehouseDestroyView',
    
    # StockItem views
    'StockItemListView', 'StockItemCreateView',
    'StockItemRetrieveView', 'StockItemUpdateView', 'StockItemDestroyView',
    
    # StockMovement views
    'StockMovementListView', 'StockMovementCreateView', 'StockMovementRetrieveView',
    
    # InventoryAuditLog views
    'InventoryAuditLogListView', 'InventoryAuditLogRetrieveView'
]
