"""
Pages views initialization file
"""
# Page views
from .page import (
    PageListCreateView,
    PageRetrieveUpdateDestroyBySlugView
)

# Banner views
from .banner import (
    BannerListCreateView
)

# Menu views
from .menu import (
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
