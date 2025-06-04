from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    ShippingMethodViewSet, ShippingZoneViewSet, 
    ShippingRateViewSet, ShipmentViewSet
)

# Legacy imports for backward compatibility
from . import views

app_name = 'shipping'

# Thiết lập router cho ViewSets
router = DefaultRouter(trailing_slash=False)
router.register(r'methods', ShippingMethodViewSet, basename='shipping-method')
router.register(r'zones', ShippingZoneViewSet, basename='shipping-zone')
router.register(r'rates', ShippingRateViewSet, basename='shipping-rate')
router.register(r'shipments', ShipmentViewSet, basename='shipment')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Shipping Methods - DEPRECATED
    path('/old/methods', views.ShippingMethodListView.as_view(), name='shipping-method-list-legacy'),
    path('/old/methods/create', views.ShippingMethodCreateView.as_view(), name='shipping-method-create-legacy'),
    path('/old/methods/<int:pk>', views.ShippingMethodRetrieveView.as_view(), name='shipping-method-detail-legacy'),
    path('/old/methods/<int:pk>/update', views.ShippingMethodUpdateView.as_view(), name='shipping-method-update-legacy'),
    path('/old/methods/<int:pk>/delete', views.ShippingMethodDestroyView.as_view(), name='shipping-method-delete-legacy'),
    
    # Shipping Zones - DEPRECATED
    path('/old/zones', views.ShippingZoneListView.as_view(), name='shipping-zone-list-legacy'),
    path('/old/zones/create', views.ShippingZoneCreateView.as_view(), name='shipping-zone-create-legacy'),
    path('/old/zones/<int:pk>', views.ShippingZoneRetrieveView.as_view(), name='shipping-zone-detail-legacy'),
    path('/old/zones/<int:pk>/update', views.ShippingZoneUpdateView.as_view(), name='shipping-zone-update-legacy'),
    path('/old/zones/<int:pk>/delete', views.ShippingZoneDestroyView.as_view(), name='shipping-zone-delete-legacy'),
    
    # Shipping Rates - DEPRECATED
    path('/old/rates', views.ShippingRateListView.as_view(), name='shipping-rate-list-legacy'),
    path('/old/rates/create', views.ShippingRateCreateView.as_view(), name='shipping-rate-create-legacy'),
    path('/old/rates/<int:pk>', views.ShippingRateRetrieveView.as_view(), name='shipping-rate-detail-legacy'),
    path('/old/rates/<int:pk>/update', views.ShippingRateUpdateView.as_view(), name='shipping-rate-update-legacy'),
    path('/old/rates/<int:pk>/delete', views.ShippingRateDestroyView.as_view(), name='shipping-rate-delete-legacy'),
    path('/old/calculate', views.CalculateShippingRatesView.as_view(), name='calculate-shipping-legacy'),
    
    # Shipments - DEPRECATED
    path('/old/shipments', views.ShipmentListView.as_view(), name='shipment-list-legacy'),
    path('/old/shipments/<int:pk>', views.ShipmentDetailView.as_view(), name='shipment-detail-legacy'),
    path('/old/shipments/order/<int:order_id>', views.ShipmentByOrderView.as_view(), name='shipment-by-order-legacy'),
    path('/old/shipments/create', views.CreateShipmentView.as_view(), name='create-shipment-legacy'),
    path('/old/shipments/<int:shipment_id>/tracking', views.AddTrackingInfoView.as_view(), name='add-tracking-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]