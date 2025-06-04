from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CustomerViewSet,
    CustomerSelfViewSet,
    CustomerGroupViewSet,
    CustomerAddressViewSet,
    CustomerAddressAdminViewSet,
    CustomerActivityViewSet,
    CustomerSelfActivityViewSet
)

app_name = 'customers'

# Router chính
router = DefaultRouter(trailing_slash=False)

# Admin endpoints
router.register(r'admin', CustomerViewSet, basename='customer-admin')
router.register(r'groups', CustomerGroupViewSet, basename='customer-group')
router.register(r'addresses', CustomerAddressAdminViewSet, basename='customer-address-admin')
router.register(r'activities', CustomerActivityViewSet, basename='customer-activity')

# URL patterns
urlpatterns = [
    # Admin router URLs
    path('', include(router.urls)),
    
    # Customer self-management endpoints
    # /api/v1/customers/me/ - Customer profile management
    path('me/', CustomerSelfViewSet.as_view({
        'get': 'list',      # GET /api/v1/customers/me/ - Get profile
        'post': 'create',   # POST /api/v1/customers/me/ - Create profile 
        'put': 'update',    # PUT /api/v1/customers/me/ - Update profile
        'patch': 'partial_update'  # PATCH /api/v1/customers/me/ - Partial update
    }), name='customer-self'),
    
    # Customer addresses management
    # /api/v1/customers/me/addresses/
    path('me/addresses/', CustomerAddressViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='customer-self-addresses-list'),
    
    path('me/addresses/<int:pk>/', CustomerAddressViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='customer-self-addresses-detail'),
    
    # Customer addresses custom actions
    path('me/addresses/default_shipping/', CustomerAddressViewSet.as_view({
        'get': 'default_shipping'
    }), name='customer-self-addresses-default-shipping'),
    
    path('me/addresses/default_billing/', CustomerAddressViewSet.as_view({
        'get': 'default_billing'
    }), name='customer-self-addresses-default-billing'),
    
    # Customer self activities
    # /api/v1/customers/me/activities/
    path('me/activities/', CustomerSelfActivityViewSet.as_view({
        'get': 'list'
    }), name='customer-self-activities-list'),
    
    path('me/activities/<int:pk>/', CustomerSelfActivityViewSet.as_view({
        'get': 'retrieve'
    }), name='customer-self-activities-detail'),
]
