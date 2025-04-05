"""
Shipping views initialization file
"""
# Shipping Method views
from .shipping_method import (
    ShippingMethodListView, ShippingMethodCreateView,
    ShippingMethodRetrieveView, ShippingMethodUpdateView, ShippingMethodDestroyView
)

# Shipping Zone views
from .shipping_zone import (
    ShippingZoneListView, ShippingZoneCreateView,
    ShippingZoneRetrieveView, ShippingZoneUpdateView, ShippingZoneDestroyView
)

# Shipping Rate views
from .shipping_rate import (
    ShippingRateListView, ShippingRateCreateView,
    ShippingRateRetrieveView, ShippingRateUpdateView, ShippingRateDestroyView,
    CalculateShippingRatesView
)

# Shipment views
from .shipment import (
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
