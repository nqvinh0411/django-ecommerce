from django.urls import path

from .views import NotificationListView, NotificationDeleteView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),
]
