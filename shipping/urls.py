from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Shipping Methods
    path('methods', views.ShippingMethodListView.as_view(), name='shipping-method-list'),
    path('methods/create', views.ShippingMethodCreateView.as_view(), name='shipping-method-create'),
    path('methods/<int:pk>', views.ShippingMethodRetrieveView.as_view(), name='shipping-method-detail'),
    path('methods/<int:pk>/update', views.ShippingMethodUpdateView.as_view(), name='shipping-method-update'),
    path('methods/<int:pk>/delete', views.ShippingMethodDestroyView.as_view(), name='shipping-method-delete'),
    
    # Shipping Zones
    path('zones', views.ShippingZoneListView.as_view(), name='shipping-zone-list'),
    path('zones/create', views.ShippingZoneCreateView.as_view(), name='shipping-zone-create'),
    path('zones/<int:pk>', views.ShippingZoneRetrieveView.as_view(), name='shipping-zone-detail'),
    path('zones/<int:pk>/update', views.ShippingZoneUpdateView.as_view(), name='shipping-zone-update'),
    path('zones/<int:pk>/delete', views.ShippingZoneDestroyView.as_view(), name='shipping-zone-delete'),
    
    # Shipping Rates
    path('rates', views.ShippingRateListView.as_view(), name='shipping-rate-list'),
    path('rates/create', views.ShippingRateCreateView.as_view(), name='shipping-rate-create'),
    path('rates/<int:pk>', views.ShippingRateRetrieveView.as_view(), name='shipping-rate-detail'),
    path('rates/<int:pk>/update', views.ShippingRateUpdateView.as_view(), name='shipping-rate-update'),
    path('rates/<int:pk>/delete', views.ShippingRateDestroyView.as_view(), name='shipping-rate-delete'),
    
    # Calculate shipping rates
    path('calculate', views.CalculateShippingRatesView.as_view(), name='calculate-shipping'),
    
    # Shipments
    path('shipments', views.ShipmentListView.as_view(), name='shipment-list'),
    path('shipments/<int:pk>', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('shipments/order/<int:order_id>', views.ShipmentByOrderView.as_view(), name='shipment-by-order'),
    path('shipments/create', views.CreateShipmentView.as_view(), name='create-shipment'),
    
    # Tracking
    path('shipments/<int:shipment_id>/tracking', views.AddTrackingInfoView.as_view(), name='add-tracking'),
]