from django.urls import path

from .views import NotificationListView, NotificationCreateView, NotificationUpdateView, NotificationDeleteView

app_name = 'notifications'

urlpatterns = [
    # Liệt kê tất cả thông báo của người dùng hiện tại
    path('/getAll', NotificationListView.as_view(), name='notification-list'),
    
    # Tạo một thông báo cụ thể
    path('/<int:pk>/create', NotificationCreateView.as_view(), name='notification-create'),

    # Cập nhật một thông báo cụ thể
    path('/<int:pk>/update', NotificationUpdateView.as_view(), name='notification-update'),

    # Xóa một thông báo cụ thể
    path('/<int:pk>/delete', NotificationDeleteView.as_view(), name='notification-delete'),
]
