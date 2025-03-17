from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from orders.models import Order, OrderItem
from products.models import Product, Category
from cart.models import Cart, CartItem

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(name="Laptop", description="Gaming Laptop", price=1200, category=self.category, stock=10)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        """Test tạo đơn hàng từ giỏ hàng"""
        response = self.client.post("/api/orders/create/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_orders(self):
        """Test lấy danh sách đơn hàng"""
        self.client.post("/api/orders/create/")
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_status(self):
        """Test cập nhật trạng thái đơn hàng (chỉ admin hoặc seller)"""
        self.client.post("/api/orders/create/")
        order = Order.objects.first()
        data = {"status": "shipped"}
        response = self.client.put(f"/api/orders/{order.id}/update-status/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Vì buyer không thể cập nhật trạng thái đơn hàng
