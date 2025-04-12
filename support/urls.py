from django.urls import path
from .views import (
    SupportTicketListCreateView,
    SupportTicketRetrieveUpdateView,
    TicketReplyCreateView,
    AdminSupportTicketListView,
    FAQListView,
    SupportCategoryListView,
)

app_name = "support"

urlpatterns = [
    # Support tickets - GET (list), POST (create)
    path('/tickets', SupportTicketListCreateView.as_view(), name='support-ticket-list'),
    
    # Support ticket detail - GET (retrieve), PUT/PATCH (update)
    path('/tickets/<int:ticket_id>', SupportTicketRetrieveUpdateView.as_view(), name='support-ticket-detail'),
    
    # Ticket reply - POST (create)
    path('/tickets/<int:ticket_id>/reply', TicketReplyCreateView.as_view(), name='ticket-reply'),
    
    # Admin ticket list - GET (list with extended admin functionality)
    path('/admin/tickets', AdminSupportTicketListView.as_view(), name='admin-ticket-list'),
    
    # FAQs - GET (list)
    path('/faqs', FAQListView.as_view(), name='faq-list'),
    
    # Support categories - GET (list)
    path('/categories', SupportCategoryListView.as_view(), name='support-category-list'),
]
