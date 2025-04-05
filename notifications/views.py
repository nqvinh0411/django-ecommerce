"""
Notifications views module - exports all view classes for the notifications app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
from .views.list import NotificationListView
from .views.delete import NotificationDeleteView

__all__ = [
    'NotificationListView',
    'NotificationDeleteView'
]
