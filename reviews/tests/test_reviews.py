from django.contrib.auth import get_user_model
from products.models import Product, Category
from rest_framework import status
from rest_framework.test import APITestCase
from reviews.models import Review

User = get_user_model()


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(name="Laptop", description="Gaming Laptop", price=1200,
                                              category=self.category, stock=10)
        self.client.force_authenticate(user=self.user)

    def test_add_review(self):
        """Test thêm đánh giá sản phẩm"""
        data = {"product_id": self.product.id, "rating": 5, "comment": "Sản phẩm rất tốt!"}
        response = self.client.post("/api/reviews/add/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_product_reviews(self):
        """Test lấy danh sách đánh giá của sản phẩm"""
        self.client.post("/api/reviews/add/", {"product_id": self.product.id, "rating": 5, "comment": "Sản phẩm tốt!"})
        response = self.client.get(f"/api/reviews/{self.product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
