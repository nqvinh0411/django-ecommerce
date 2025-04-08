"""
Notifications views initialization file
"""
from .list import NotificationListView
from .create import NotificationCreateView
from .update import NotificationUpdateView
from .delete import NotificationDeleteView

__all__ = [
    'NotificationListView',
    'NotificationCreateView',
    'NotificationUpdateView',
    'NotificationDeleteView'
]
