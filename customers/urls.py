from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'groups', views.CustomerGroupViewSet, basename='customer-group')
router.register(r'addresses', views.CustomerAddressViewSet, basename='customer-address')
router.register(r'activities', views.CustomerActivityViewSet, basename='customer-activity')

app_name = 'customers'

urlpatterns = [
    path('', include(router.urls)),
]