from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import UsageLogViewSet

app_name = 'usage_logs'

# Tạo router cho Usage Logs API
router = DefaultRouter()
router.register('', UsageLogViewSet, basename='usage-log')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 