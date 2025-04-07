from django.urls import path

from .views import (
    RegisterView, LogoutView, UserDetailView,
    CustomTokenObtainPairView, UserSessionListView,
    UserSessionDeleteView, LogoutOtherSessionsView,
    UserLoginHistoryListView, TokenRefreshView,
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register', RegisterView.as_view(), name='register'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User endpoints
    path('me', UserDetailView.as_view(), name='user-detail'),
    
    # Session management
    path('sessions', UserSessionListView.as_view(), name='session-list'),
    path('sessions/<int:session_id>', UserSessionDeleteView.as_view(), name='session-delete'),
    path('sessions/logout-others', LogoutOtherSessionsView.as_view(), name='session-logout-others'),
    path('login-history', UserLoginHistoryListView.as_view(), name='login-history'),
]
