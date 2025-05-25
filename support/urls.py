from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    SupportCategoryViewSet, SupportTicketViewSet,
    TicketReplyViewSet, FAQViewSet
)

# Legacy imports for backward compatibility
from .views import (
    SupportTicketListCreateView,
    SupportTicketRetrieveUpdateView,
    TicketReplyCreateView,
    AdminSupportTicketListView,
    FAQListView,
    SupportCategoryListView,
)

app_name = "support"

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'categories', SupportCategoryViewSet, basename='support-category')
router.register(r'tickets', SupportTicketViewSet, basename='support-ticket')
router.register(r'replies', TicketReplyViewSet, basename='ticket-reply')
router.register(r'faqs', FAQViewSet, basename='faq')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Legacy support endpoints - DEPRECATED
    path('/old/tickets', SupportTicketListCreateView.as_view(), name='support-ticket-list-legacy'),
    path('/old/tickets/<int:ticket_id>', SupportTicketRetrieveUpdateView.as_view(), name='support-ticket-detail-legacy'),
    path('/old/tickets/<int:ticket_id>/reply', TicketReplyCreateView.as_view(), name='ticket-reply-legacy'),
    path('/old/admin/tickets', AdminSupportTicketListView.as_view(), name='admin-ticket-list-legacy'),
    path('/old/faqs', FAQListView.as_view(), name='faq-list-legacy'),
    path('/old/categories', SupportCategoryListView.as_view(), name='support-category-list-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
