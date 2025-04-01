from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'attributes', views.AttributeViewSet, basename='attribute')
router.register(r'attribute-values', views.AttributeValueViewSet, basename='attribute-value')

app_name = 'catalog'

urlpatterns = [
    path('', include(router.urls)),
]