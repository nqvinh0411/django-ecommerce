"""
Support views module - exports all view classes for the support app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
# Support Category views
from .views.category import SupportCategoryListView

# Support Ticket views
from .views.ticket import (
    SupportTicketListCreateView,
    SupportTicketRetrieveUpdateView,
    TicketReplyCreateView
)

# Admin views
from .views.admin import AdminSupportTicketListView

# FAQ views
from .views.faq import FAQListView

__all__ = [
    # Support Category views
    'SupportCategoryListView',
    
    # Support Ticket views
    'SupportTicketListCreateView',
    'SupportTicketRetrieveUpdateView',
    'TicketReplyCreateView',
    
    # Admin views
    'AdminSupportTicketListView',
    
    # FAQ views
    'FAQListView'
]
