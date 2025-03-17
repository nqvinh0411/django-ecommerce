from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from payments.models import Payment
from orders.models import Order, OrderItem
from products.models import Product, Category

User = get_user_model()

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(name="Laptop", description="Gaming Laptop", price=1200, category=self.category, stock=10)
        self.order = Order.objects.create(user=self.user, status="pending")
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=self.product.price)
        self.client.force_authenticate(user=self.user)

    def test_checkout_payment(self):
        """Test thực hiện thanh toán"""
        data = {"order_id": self.order.id}
        response = self.client.post("/api/payments/checkout/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_payment_status(self):
        """Test kiểm tra trạng thái thanh toán"""
        self.client.post("/api/payments/checkout/", {"order_id": self.order.id})
        payment = Payment.objects.first()
        response = self.client.get(f"/api/payments/{payment.id}/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
