from django.urls import path

from .views import (
    CategoryListView, ProductListView, ProductCreateView,
    ProductDetailView, ProductUpdateView, ProductDeleteView, ProductImageUploadView
)

app_name = 'products'

urlpatterns = [
    path('categories', CategoryListView.as_view(), name='category-list'),
    path('', ProductListView.as_view(), name='product-list'),
    path('add', ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/update', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete', ProductDeleteView.as_view(), name='product-delete'),
    path('<int:product_id>/images', ProductImageUploadView.as_view(), name='product-image-upload'),
]
