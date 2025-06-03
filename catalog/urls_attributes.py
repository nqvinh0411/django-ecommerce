from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import AttributeViewSet

app_name = 'attributes'

# Tạo router cho Attributes API
router = DefaultRouter()
router.register('', AttributeViewSet, basename='attribute')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 