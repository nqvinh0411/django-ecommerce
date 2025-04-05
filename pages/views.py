"""
Pages views module - exports all view classes for the pages app.
This file follows the Single Responsibility Principle by focusing only on exporting views.
"""
from .views.page import (
    PageListCreateView,
    PageRetrieveUpdateDestroyBySlugView
)

from .views.banner import (
    BannerListCreateView
)

from .views.menu import (
    MenuListCreateView
)

__all__ = [
    # Page views
    'PageListCreateView',
    'PageRetrieveUpdateDestroyBySlugView',
    
    # Banner views
    'BannerListCreateView',
    
    # Menu views
    'MenuListCreateView'
]
