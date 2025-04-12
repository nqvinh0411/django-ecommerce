from django.urls import path

from .views import (
    CategoryListCreateView, ProductListView, ProductCreateView,
    ProductRetrieveView, ProductUpdateView, ProductDestroyView, ProductImageUploadView
)

app_name = 'products'

urlpatterns = [
    # Category endpoints
    path('/categories', CategoryListCreateView.as_view(), name='category-list-create'),

    # Product endpoints
    path('', ProductListView.as_view(), name='product-list'),
    path('/create', ProductCreateView.as_view(), name='product-create'),
    path('/<int:pk>/view', ProductRetrieveView.as_view(), name='product-detail'),
    path('/<int:pk>/update', ProductUpdateView.as_view(), name='product-update'),
    path('/<int:pk>/delete', ProductDestroyView.as_view(), name='product-delete'),
    
    # Product image endpoints
    path('/<int:product_id>/images/upload', ProductImageUploadView.as_view(), name='product-image-upload'),
]
