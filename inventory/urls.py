from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    WarehouseViewSet,
    StockItemViewSet,
    StockMovementViewSet,
    InventoryAuditLogViewSet
)

app_name = 'inventory'

# Tạo router cho Inventory API
router = DefaultRouter(trailing_slash=False)
router.register('warehouses', WarehouseViewSet, basename='warehouse')
router.register('stock-items', StockItemViewSet, basename='stock-item')
router.register('stock-movements', StockMovementViewSet, basename='stock-movement')
router.register('audit-logs', InventoryAuditLogViewSet, basename='inventory-audit-log')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
