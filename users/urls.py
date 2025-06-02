from django.urls import path
from .views import UserDetailView, UserProfileUpdateView

app_name = 'users'

urlpatterns = [
    # User Profile Management
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('me/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
]
