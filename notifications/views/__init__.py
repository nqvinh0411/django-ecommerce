"""
Notifications views initialization file
"""
from .list import NotificationListView
from .delete import NotificationDeleteView

__all__ = [
    'NotificationListView',
    'NotificationDeleteView'
]
