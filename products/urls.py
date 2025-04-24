from django.urls import path

from .views import (
    ProductListView, ProductCreateView,
    ProductRetrieveView, ProductUpdateView, ProductDestroyView, ProductImageUploadView
)

app_name = 'products'

urlpatterns = [
    # Product endpoints
    path('', ProductListView.as_view(), name='list'),
    path('/create', ProductCreateView.as_view(), name='create'),
    path('/<int:pk>/view', ProductRetrieveView.as_view(), name='detail'),
    path('/<int:pk>/update', ProductUpdateView.as_view(), name='update'),
    path('/<int:pk>/delete', ProductDestroyView.as_view(), name='delete'),

    # Product image endpoints
    path('/<int:product_id>/images/upload', ProductImageUploadView.as_view(), name='image-upload'),
]
