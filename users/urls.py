from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import UserViewSet

app_name = 'users'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # ViewSets URL patterns - API chuẩn hóa
    path('', include(router.urls)),
]
