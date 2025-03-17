from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Category

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="password", is_seller=True)
        self.category = Category.objects.create(name="Electronics")
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        """Test tạo sản phẩm mới"""
        data = {"name": "Laptop", "description": "Gaming Laptop", "price": 1200, "category": self.category.id, "stock": 10}
        response = self.client.post("/api/products/add/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_without_authentication(self):
        """Test tạo sản phẩm khi chưa đăng nhập"""
        self.client.logout()
        data = {"name": "Laptop", "description": "Gaming Laptop", "price": 1200, "category": self.category.id, "stock": 10}
        response = self.client.post("/api/products/add/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_products(self):
        """Test lấy danh sách sản phẩm"""
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product(self):
        """Test cập nhật sản phẩm"""
        product = Product.objects.create(name="Old Laptop", description="Old model", price=1000, category=self.category, seller=self.user)
        data = {"name": "Updated Laptop", "price": 1400, "stock": 8}
        response = self.client.put(f"/api/products/{product.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
