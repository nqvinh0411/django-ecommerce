"""
Settings views module - exports all view classes for the settings app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
# Store settings views
from .views.store import StoreSettingView

# Currency views
from .views.currency import CurrencyListView

# Language views
from .views.language import LanguageSettingListView

# Email template views
from .views.email_template import (
    EmailTemplateListCreateView,
    EmailTemplateRetrieveUpdateDestroyView
)

__all__ = [
    # Store settings views
    'StoreSettingView',
    
    # Currency views
    'CurrencyListView',
    
    # Language views
    'LanguageSettingListView',
    
    # Email template views
    'EmailTemplateListCreateView',
    'EmailTemplateRetrieveUpdateDestroyView'
]
