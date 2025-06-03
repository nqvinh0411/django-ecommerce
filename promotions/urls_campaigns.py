from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import PromotionCampaignViewSet

app_name = 'campaigns'

# Tạo router cho Promotion Campaigns API
router = DefaultRouter()
router.register('', PromotionCampaignViewSet, basename='campaign')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 