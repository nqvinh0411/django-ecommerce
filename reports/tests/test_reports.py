from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, datetime
from customers.models import Customer
from products.models import Product, Category
from reports.models import SalesReport, ProductReport, CustomerReport, TrafficLog

User = get_user_model()


class ReportsModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create admin user
        cls.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        cls.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        cls.customer = Customer.objects.create(user=cls.regular_user)
        
        # Create category and product
        cls.category = Category.objects.create(name='Test Category')
        cls.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=cls.category,
            seller_id=cls.admin_user,
            stock=10
        )
        
        # Create reports
        cls.sales_report = SalesReport.objects.create(
            date=date.today(),
            total_orders=10,
            total_revenue=999.90,
            total_discount=99.99,
            net_revenue=899.91
        )
        
        cls.product_report = ProductReport.objects.create(
            product=cls.product,
            sold_quantity=5,
            total_revenue=499.95,
            average_rating=4.5,
            last_sold_at=datetime.now()
        )
        
        cls.customer_report = CustomerReport.objects.create(
            customer=cls.customer,
            total_orders=3,
            total_spent=299.97,
            average_order_value=99.99,
            last_order_at=datetime.now()
        )
        
        cls.traffic_log = TrafficLog.objects.create(
            endpoint='/api/products/',
            method='GET',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            duration_ms=150
        )

    def setUp(self):
        # Create API client for each test
        self.client = APIClient()

    def test_sales_report_model(self):
        """Test the SalesReport model"""
        self.assertEqual(str(self.sales_report), f"Sales Report {date.today()}")
        self.assertEqual(self.sales_report.total_orders, 10)
        self.assertEqual(self.sales_report.total_revenue, 999.90)
        self.assertEqual(self.sales_report.total_discount, 99.99)
        self.assertEqual(self.sales_report.net_revenue, 899.91)

    def test_product_report_model(self):
        """Test the ProductReport model"""
        self.assertEqual(str(self.product_report), f"Report for {self.product.name}")
        self.assertEqual(self.product_report.product, self.product)
        self.assertEqual(self.product_report.sold_quantity, 5)
        self.assertEqual(self.product_report.total_revenue, 499.95)
        self.assertEqual(self.product_report.average_rating, 4.5)

    def test_customer_report_model(self):
        """Test the CustomerReport model"""
        self.assertEqual(str(self.customer_report), f"Report for {self.customer.user.email}")
        self.assertEqual(self.customer_report.customer, self.customer)
        self.assertEqual(self.customer_report.total_orders, 3)
        self.assertEqual(self.customer_report.total_spent, 299.97)
        self.assertEqual(self.customer_report.average_order_value, 99.99)

    def test_traffic_log_model(self):
        """Test the TrafficLog model"""
        self.assertEqual(
            str(self.traffic_log),
            f"GET /api/products/ - 150ms"
        )
        self.assertEqual(self.traffic_log.endpoint, '/api/products/')
        self.assertEqual(self.traffic_log.method, 'GET')
        self.assertEqual(self.traffic_log.ip_address, '127.0.0.1')
        self.assertEqual(self.traffic_log.duration_ms, 150)


class ReportsAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create admin user
        cls.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        cls.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        
        # Create reports data
        SalesReport.objects.create(
            date=date.today(),
            total_orders=10,
            total_revenue=999.90,
            total_discount=99.99,
            net_revenue=899.91
        )

    def setUp(self):
        # Set up API client for each test
        self.client = APIClient()

    def test_sales_report_endpoint_admin_access(self):
        """Admin users can access the sales report endpoint"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('sales-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sales_report_endpoint_non_admin_denied(self):
        """Non-admin users cannot access the sales report endpoint"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('sales-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reports_endpoint_unauthenticated_denied(self):
        """Unauthenticated users cannot access the reports endpoint"""
        url = reverse('sales-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
