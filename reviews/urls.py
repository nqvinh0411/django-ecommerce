from django.urls import path

from .views import AddReviewView, ProductReviewsView

urlpatterns = [
    path('add/', AddReviewView.as_view(), name='add-review'),
    path('<int:product_id>/', ProductReviewsView.as_view(), name='product-reviews'),
]
