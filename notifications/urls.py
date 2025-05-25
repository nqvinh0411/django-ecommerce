from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import NotificationViewSet

# Legacy imports for backward compatibility
from .views import NotificationListView, NotificationCreateView, NotificationUpdateView, NotificationDeleteView

app_name = 'notifications'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Notification endpoints - DEPRECATED
    path('/old/getAll', NotificationListView.as_view(), name='notification-list-legacy'),
    path('/old/<int:pk>/create', NotificationCreateView.as_view(), name='notification-create-legacy'),
    path('/old/<int:pk>/update', NotificationUpdateView.as_view(), name='notification-update-legacy'),
    path('/old/<int:pk>/delete', NotificationDeleteView.as_view(), name='notification-delete-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
