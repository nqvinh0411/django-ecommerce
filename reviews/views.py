from products.models import Product
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review
from .serializers import ReviewSerializer


# API Thêm đánh giá cho sản phẩm
class AddReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        if not rating or not (1 <= int(rating) <= 5):
            return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={"rating": rating, "comment": comment}
            )
            return Response({"message": "Review added successfully"}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


# API Lấy danh sách đánh giá của sản phẩm
class ProductReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)
