from django.urls import path
from .views import (
    StoreSettingView,
    CurrencyListView,
    LanguageSettingListView,
    EmailTemplateListCreateView,
    EmailTemplateDetailView
)

urlpatterns = [
    path('store/', StoreSettingView.as_view(), name='store-setting'),
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('languages/', LanguageSettingListView.as_view(), name='language-list'),
    path('emails/', EmailTemplateListCreateView.as_view(), name='email-template-list'),
    path('emails/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
]
