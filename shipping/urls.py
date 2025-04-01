from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Shipping Methods
    path('methods/', views.ShippingMethodListCreateView.as_view(), name='shipping-method-list'),
    path('methods/<int:pk>/', views.ShippingMethodDetailView.as_view(), name='shipping-method-detail'),
    
    # Shipping Zones
    path('zones/', views.ShippingZoneListCreateView.as_view(), name='shipping-zone-list'),
    path('zones/<int:pk>/', views.ShippingZoneDetailView.as_view(), name='shipping-zone-detail'),
    
    # Shipping Rates
    path('rates/', views.ShippingRateListCreateView.as_view(), name='shipping-rate-list'),
    path('rates/<int:pk>/', views.ShippingRateDetailView.as_view(), name='shipping-rate-detail'),
    
    # Calculate shipping rates
    path('calculate/', views.CalculateShippingRatesView.as_view(), name='calculate-shipping'),
    
    # Shipments
    path('shipments/', views.ShipmentListView.as_view(), name='shipment-list'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('shipments/order/<int:order_id>/', views.ShipmentByOrderView.as_view(), name='shipment-by-order'),
    path('shipments/create/', views.CreateShipmentView.as_view(), name='create-shipment'),
    
    # Tracking
    path('shipments/<int:shipment_id>/tracking/', views.AddTrackingInfoView.as_view(), name='add-tracking'),
]