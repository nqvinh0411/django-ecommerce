from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CustomerViewSet,
    CustomerGroupViewSet,
    CustomerAddressViewSet,
    CustomerActivityViewSet
)

# Legacy imports for backward compatibility
from .views import (
    # Customer views
    CustomerListCreateView, CustomerRetrieveUpdateDestroyView,
    # CustomerGroup views
    CustomerGroupListCreateView, CustomerGroupRetrieveUpdateDestroyView,
    # CustomerAddress views
    CustomerAddressListCreateView, CustomerAddressRetrieveUpdateDestroyView,
    CustomerAddressDefaultShippingView, CustomerAddressDefaultBillingView,
    # CustomerActivity views
    CustomerActivityListView, CustomerActivityRetrieveView
)

app_name = 'customers'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customer')
router.register(r'groups', CustomerGroupViewSet, basename='customer-group')
router.register(r'addresses', CustomerAddressViewSet, basename='customer-address')
router.register(r'activities', CustomerActivityViewSet, basename='customer-activity')

# URL patterns cho router và các views khác
urlpatterns = [
    # ViewSets URL patterns
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Customer endpoints - DEPRECATED
    path('/old/list', CustomerListCreateView.as_view(), name='customer-list-legacy'),
    path('/old/create', CustomerListCreateView.as_view(), name='customer-create-legacy'),
    path('/old/<int:pk>', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-detail-legacy'),
    path('/old/<int:pk>/update', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-update-legacy'),
    path('/old/<int:pk>/delete', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-delete-legacy'),

    # CustomerGroup endpoints - DEPRECATED
    path('/old/groups', CustomerGroupListCreateView.as_view(), name='customer-group-list-create-legacy'),
    path('/old/groups/create', CustomerGroupListCreateView.as_view(), name='customer-group-list-create-legacy'),
    path('/old/groups/<int:pk>', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-detail-legacy'),
    path('/old/groups/<int:pk>/update', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-update-legacy'),
    path('/old/groups/<int:pk>/delete', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-delete-legacy'),

    # CustomerAddress endpoints - DEPRECATED
    path('/old/addresses', CustomerAddressListCreateView.as_view(), name='customer-address-list-create-legacy'),
    path('/old/addresses/create', CustomerAddressListCreateView.as_view(), name='customer-address-list-create-legacy'),
    path('/old/addresses/<int:pk>', CustomerAddressRetrieveUpdateDestroyView.as_view(), name='customer-address-detail-legacy'),
    path('/old/addresses/<int:pk>/update', CustomerAddressRetrieveUpdateDestroyView.as_view(), name='customer-address-update-legacy'),
    path('/old/addresses/<int:pk>/delete', CustomerAddressRetrieveUpdateDestroyView.as_view(), name='customer-address-delete-legacy'),
    
    # CustomerActivity endpoints - DEPRECATED
    path('/old/activities', CustomerActivityListView.as_view(), name='customer-activity-list-legacy'),
    path('/old/activities/<int:pk>', CustomerActivityRetrieveView.as_view(), name='customer-activity-detail-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
