from django.urls import path
from .views import (
    SupportTicketListCreateView,
    SupportTicketDetailView,
    TicketReplyCreateView,
    AdminSupportTicketListView,
    FAQListView,
    SupportCategoryListView,
)

app_name = "support"

urlpatterns = [
    path('tickets', SupportTicketListCreateView.as_view(), name='support-ticket-list'),
    path('tickets/<int:ticket_id>', SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('tickets/<int:ticket_id>/reply', TicketReplyCreateView.as_view(), name='ticket-reply'),
    path('admin/tickets', AdminSupportTicketListView.as_view(), name='admin-ticket-list'),
    path('faqs', FAQListView.as_view(), name='faq-list'),
    path('categories', SupportCategoryListView.as_view(), name='support-category-list'),
]
