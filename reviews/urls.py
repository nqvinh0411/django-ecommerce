from django.urls import path

from .views import (
    ReviewCreateView, ProductReviewListView, 
    UserReviewListView, ReviewDetailView
)

app_name = 'reviews'

urlpatterns = [
    # Endpoints cho đánh giá sản phẩm
    path('', ReviewCreateView.as_view(), name='review-create'),
    path('products/<int:product_id>', ProductReviewListView.as_view(), name='product-reviews'),
    path('my-reviews', UserReviewListView.as_view(), name='user-reviews'),
    path('<int:review_id>', ReviewDetailView.as_view(), name='review-detail'),
]
