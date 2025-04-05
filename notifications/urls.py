from django.urls import path

from .views import NotificationListView, NotificationDeleteView

app_name = 'notifications'

urlpatterns = [
    # Liệt kê tất cả thông báo của người dùng hiện tại
    path('', NotificationListView.as_view(), name='notification-list'),
    
    # Xóa một thông báo cụ thể
    path('<int:pk>/delete', NotificationDeleteView.as_view(), name='notification-delete'),
]
