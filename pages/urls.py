from django.urls import path
from .views import (
    PageListView,
    PageDetailBySlugView,
    BannerListView,
    MenuListView
)

app_name = "pages"

urlpatterns = [
    path('pages', PageListView.as_view(), name='page-list'),
    path('pages/<slug:slug>', PageDetailBySlugView.as_view(), name='page-detail'),
    path('banners', BannerListView.as_view(), name='banner-list'),
    path('menus/<str:menu_type>', MenuListView.as_view(), name='menu-list'),
]
