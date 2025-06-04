from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Legacy views (backward compatibility)
    UserDetailView, 
    UserProfileUpdateView,
    # New ViewSets
    UserAdminViewSet,
    UserSelfViewSet,
    UserRoleViewSet
)

app_name = 'users'

# Router cho các ViewSets
router = DefaultRouter(trailing_slash=False)

# Admin user management
router.register(r'admin', UserAdminViewSet, basename='user-admin')

# Role management
router.register(r'roles', UserRoleViewSet, basename='user-role')

urlpatterns = [
    # =============================================================================
    # LEGACY ENDPOINTS (backward compatibility)
    # =============================================================================
    # User Profile Management - legacy
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('me/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # =============================================================================
    # NEW VIEWSET ENDPOINTS
    # =============================================================================
    # Router URLs - includes admin and roles viewsets
    path('', include(router.urls)),
    
    # User self-management endpoints (modern approach)
    # /api/v1/users/profile/ - User self profile management
    path('profile/', UserSelfViewSet.as_view({
        'get': 'list',           # GET /api/v1/users/profile/ - Get profile
        'put': 'update',         # PUT /api/v1/users/profile/ - Update profile
        'patch': 'partial_update' # PATCH /api/v1/users/profile/ - Partial update
    }), name='user-self-profile'),
    
    # User self-management custom actions
    path('profile/upload-avatar/', UserSelfViewSet.as_view({
        'post': 'upload_avatar'  # POST /api/v1/users/profile/upload-avatar/ - Upload avatar
    }), name='user-self-upload-avatar'),
    
    path('profile/change-password/', UserSelfViewSet.as_view({
        'post': 'change_password' # POST /api/v1/users/profile/change-password/ - Change password
    }), name='user-self-change-password'),
    
    path('profile/activity/', UserSelfViewSet.as_view({
        'get': 'activity'        # GET /api/v1/users/profile/activity/ - Activity log
    }), name='user-self-activity'),
]
