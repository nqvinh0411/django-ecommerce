from django.urls import path
from .views import (
    PageListCreateView,
    PageRetrieveUpdateDestroyBySlugView,
    BannerListCreateView,
    MenuListCreateView
)

app_name = "pages"

urlpatterns = [
    # Pages - GET (list), POST (create)
    path('', PageListCreateView.as_view(), name='page-list'),
    
    # Page detail - GET (retrieve), PUT/PATCH (update), DELETE (destroy)
    path('/<slug:slug>', PageRetrieveUpdateDestroyBySlugView.as_view(), name='page-detail'),
    
    # Banners - GET (list), POST (create)
    path('/banners', BannerListCreateView.as_view(), name='banner-list'),
    
    # Menus - GET (list), POST (create)
    path('/menus/<str:menu_type>', MenuListCreateView.as_view(), name='menu-list'),
]
