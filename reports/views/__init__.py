"""
Reports views initialization file
"""
# Sales report views
from .sales import SalesReportListView

# Product report views
from .product import ProductReportListView

# Customer report views
from .customer import CustomerReportListView

# Traffic log views
from .traffic import TrafficLogListView

__all__ = [
    # Sales report views
    'SalesReportListView',
    
    # Product report views
    'ProductReportListView',
    
    # Customer report views
    'CustomerReportListView',
    
    # Traffic log views
    'TrafficLogListView'
]
