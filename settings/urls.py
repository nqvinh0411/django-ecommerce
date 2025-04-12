from django.urls import path
from .views import (
    StoreSettingView,
    CurrencyListView,
    LanguageSettingListView,
    EmailTemplateListCreateView,
    EmailTemplateRetrieveUpdateDestroyView
)

app_name = "settings"

urlpatterns = [
    # Store settings - GET (retrieve), PUT/PATCH (update)
    path('/store', StoreSettingView.as_view(), name='store-setting'),
    
    # Currencies - GET (list)
    path('/currencies', CurrencyListView.as_view(), name='currency-list'),
    
    # Languages - GET (list)
    path('/languages', LanguageSettingListView.as_view(), name='language-list'),
    
    # Email templates - GET (list), POST (create)
    path('/emails', EmailTemplateListCreateView.as_view(), name='email-template-list'),
    
    # Email template detail - GET (retrieve), PUT/PATCH (update), DELETE (destroy)
    path('/emails/<int:pk>', EmailTemplateRetrieveUpdateDestroyView.as_view(), name='email-template-detail'),
]
