"""
Shipping views module - exports all view classes for the shipping app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
from .views.shipping_method import (
    ShippingMethodListView, ShippingMethodCreateView,
    ShippingMethodRetrieveView, ShippingMethodUpdateView, ShippingMethodDestroyView
)

from .views.shipping_zone import (
    ShippingZoneListView, ShippingZoneCreateView,
    ShippingZoneRetrieveView, ShippingZoneUpdateView, ShippingZoneDestroyView
)

from .views.shipping_rate import (
    ShippingRateListView, ShippingRateCreateView,
    ShippingRateRetrieveView, ShippingRateUpdateView, ShippingRateDestroyView,
    CalculateShippingRatesView
)

from .views.shipment import (
    ShipmentListView, ShipmentDetailView, ShipmentByOrderView, 
    CreateShipmentView, AddTrackingInfoView
)

__all__ = [
    # Shipping Method views
    'ShippingMethodListView', 'ShippingMethodCreateView',
    'ShippingMethodRetrieveView', 'ShippingMethodUpdateView', 'ShippingMethodDestroyView',
    
    # Shipping Zone views
    'ShippingZoneListView', 'ShippingZoneCreateView',
    'ShippingZoneRetrieveView', 'ShippingZoneUpdateView', 'ShippingZoneDestroyView',
    
    # Shipping Rate views
    'ShippingRateListView', 'ShippingRateCreateView',
    'ShippingRateRetrieveView', 'ShippingRateUpdateView', 'ShippingRateDestroyView',
    'CalculateShippingRatesView',
    
    # Shipment views
    'ShipmentListView', 'ShipmentDetailView', 'ShipmentByOrderView',
    'CreateShipmentView', 'AddTrackingInfoView'
]
