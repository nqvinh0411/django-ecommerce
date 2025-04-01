from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet, basename='warehouse')
router.register(r'stock-items', views.StockItemViewSet, basename='stock-item')
router.register(r'stock-movements', views.StockMovementViewSet, basename='stock-movement')
router.register(r'audit-logs', views.InventoryAuditLogViewSet, basename='inventory-audit-log')

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
]