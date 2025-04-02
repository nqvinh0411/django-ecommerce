from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from customers.models import Customer
from ..models import SupportCategory, SupportTicket, TicketReply, FAQ

User = get_user_model()


class SupportModelTests(TestCase):
    def setUp(self):
        # Create test user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890'
        )
        
        # Create support category
        self.category = SupportCategory.objects.create(
            name='Test Category',
            description='Test Description',
            is_active=True
        )
        
        # Create support ticket
        self.ticket = SupportTicket.objects.create(
            customer=self.customer,
            category=self.category,
            subject='Test Ticket',
            message='Test Message',
            status='pending'
        )

    def test_support_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_support_ticket_str(self):
        self.assertEqual(str(self.ticket), f"Test Ticket - {self.customer}")

    def test_ticket_reply_creation(self):
        reply = TicketReply.objects.create(
            ticket=self.ticket,
            user=self.user,
            message='Test Reply',
            is_staff_reply=False
        )
        self.assertEqual(reply.ticket, self.ticket)
        self.assertEqual(reply.user, self.user)
        self.assertEqual(reply.message, 'Test Reply')
        self.assertFalse(reply.is_staff_reply)

    def test_faq_creation(self):
        faq = FAQ.objects.create(
            question='Test Question',
            answer='Test Answer',
            category=self.category,
            is_published=True
        )
        self.assertEqual(faq.question, 'Test Question')
        self.assertEqual(faq.answer, 'Test Answer')
        self.assertEqual(faq.category, self.category)
        self.assertTrue(faq.is_published)


class SupportAPITests(APITestCase):
    def setUp(self):
        # Create regular user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create support category
        self.category = SupportCategory.objects.create(
            name='Test Category',
            description='Test Description',
            is_active=True
        )
        
        # Create support ticket
        self.ticket = SupportTicket.objects.create(
            customer=self.customer,
            category=self.category,
            subject='Test Ticket',
            message='Test Message',
            status='pending'
        )
        
        # Create FAQ
        self.faq = FAQ.objects.create(
            question='Test Question',
            answer='Test Answer',
            category=self.category,
            is_published=True
        )
        
        # Setup client
        self.client = APIClient()

    def test_customer_can_create_ticket(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('support-ticket-list')
        data = {
            'subject': 'New Ticket',
            'message': 'I need help',
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupportTicket.objects.count(), 2)
        self.assertEqual(SupportTicket.objects.last().subject, 'New Ticket')

    def test_customer_can_view_own_tickets(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('support-ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_reply_to_own_ticket(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('ticket-reply', kwargs={'ticket_id': self.ticket.id})
        data = {
            'message': 'My reply'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TicketReply.objects.count(), 1)
        self.assertEqual(TicketReply.objects.first().message, 'My reply')
        self.assertFalse(TicketReply.objects.first().is_staff_reply)

    def test_admin_can_view_all_tickets(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_can_view_faqs(self):
        url = reverse('faq-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], 'Test Question')
