from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model
from products.models import Product, Category
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(name="Laptop", description="Gaming Laptop", price=1200,
                                              category=self.category, stock=10)
        self.client.force_authenticate(user=self.user)

    def test_add_to_cart(self):
        """Test thêm sản phẩm vào giỏ hàng"""
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post("/api/cart/add/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_cart(self):
        """Test cập nhật số lượng sản phẩm trong giỏ hàng"""
        self.client.post("/api/cart/add/", {"product_id": self.product.id, "quantity": 1})
        data = {"product_id": self.product.id, "quantity": 3}
        response = self.client.put("/api/cart/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_from_cart(self):
        """Test xóa sản phẩm khỏi giỏ hàng"""
        self.client.post("/api/cart/add/", {"product_id": self.product.id, "quantity": 1})
        data = {"product_id": self.product.id}
        response = self.client.delete("/api/cart/remove/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
