from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    StoreSettingViewSet,
    CurrencyViewSet,
    LanguageSettingViewSet,
    EmailTemplateViewSet
)

app_name = "settings"

# Tạo router cho Settings API
router = DefaultRouter(trailing_slash=False)
router.register('store', StoreSettingViewSet, basename='store-setting')
router.register('currencies', CurrencyViewSet, basename='currency')
router.register('languages', LanguageSettingViewSet, basename='language')
router.register('email-templates', EmailTemplateViewSet, basename='email-template')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
