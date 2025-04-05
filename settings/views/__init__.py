"""
Settings views initialization file
"""
# Store settings views
from .store import StoreSettingView

# Currency views
from .currency import CurrencyListView

# Language views
from .language import LanguageSettingListView

# Email template views
from .email_template import (
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
