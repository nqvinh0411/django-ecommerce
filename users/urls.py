from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import (
    RegisterAPIView, LogoutAPIView, UserDetailAPIView,
    CustomTokenObtainPairView, UserSessionListAPIView,
    UserSessionDeleteAPIView, LogoutOtherSessionsAPIView,
    UserLoginHistoryListAPIView, AuthTokenRefreshView,
)

app_name = 'users'

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('user/info', UserDetailAPIView.as_view(), name='info'),
    path('token/refresh', AuthTokenRefreshView.as_view(), name='token_refresh'),

    path('user/sessions', UserSessionListAPIView.as_view()),
    path('user/sessions/<int:pk>', UserSessionDeleteAPIView.as_view()),
    path('user/sessions/logout_others', LogoutOtherSessionsAPIView.as_view()),
    path('user/login_history', UserLoginHistoryListAPIView.as_view()),
]
