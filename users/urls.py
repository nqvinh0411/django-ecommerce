from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import UserViewSet

# Legacy imports for backward compatibility
from .views import (
    RegisterView, LogoutView, UserDetailView,
    LoginView, UserSessionListView, CustomTokenObtainPairView,
    UserSessionDeleteView, LogoutOtherSessionsView,
    UserLoginHistoryListView, TokenRefreshView,
)

app_name = 'users'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Authentication endpoints - DEPRECATED
    path('/old/register', RegisterView.as_view(), name='register-legacy'),
    path('/old/login', CustomTokenObtainPairView.as_view(), name='login-legacy'),
    path('/old/logout', LogoutView.as_view(), name='logout-legacy'),
    path('/old/token/refresh', TokenRefreshView.as_view(), name='token-refresh-legacy'),
    
    # User endpoints - DEPRECATED
    path('/old/me', UserDetailView.as_view(), name='user-detail-legacy'),
    
    # Session management - DEPRECATED
    path('/old/sessions', UserSessionListView.as_view(), name='session-list-legacy'),
    path('/old/sessions/<int:session_id>', UserSessionDeleteView.as_view(), name='session-delete-legacy'),
    path('/old/sessions/logout-others', LogoutOtherSessionsView.as_view(), name='session-logout-others-legacy'),
    path('/old/login-history', UserLoginHistoryListView.as_view(), name='login-history-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
