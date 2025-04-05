"""
Inventory views initialization file
"""
# Warehouse views
from .warehouse import (
    WarehouseListView, WarehouseCreateView, 
    WarehouseRetrieveView, WarehouseUpdateView, WarehouseDestroyView
)

# StockItem views
from .stock_item import (
    StockItemListView, StockItemCreateView,
    StockItemRetrieveView, StockItemUpdateView, StockItemDestroyView
)

# StockMovement views
from .stock_movement import (
    StockMovementListView, StockMovementCreateView, StockMovementRetrieveView
)

# InventoryAuditLog views
from .audit_log import (
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
