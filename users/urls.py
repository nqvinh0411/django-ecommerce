from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import RegisterAPIView, LogoutAPIView, UserDetailAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/', UserDetailAPIView.as_view(), name='user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
