from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product, Category
from ..models import Wishlist, WishlistItem

User = get_user_model()


class WishlistAPITests(TestCase):
    """Test suite for Wishlist API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create user and authenticate
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create customer
        self.customer = Customer.objects.create(user=self.user)
        
        # Create category and products
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Test Product 1',
            description='Test Description 1',
            price=99.99,
            category=self.category,
            stock=10
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test Description 2',
            price=199.99,
            category=self.category,
            stock=5
        )
        
        # URLs
        self.wishlist_url = reverse('wishlist:wishlist-detail')
        self.wishlist_items_list_url = reverse('wishlist:wishlist-items-list')
        self.wishlist_items_add_url = reverse('wishlist:wishlist-items-create')
    
    def test_retrieve_wishlist(self):
        """Test retrieving a user's wishlist"""
        # Make GET request
        response = self.client.get(self.wishlist_url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in response.data)
        self.assertTrue('created_at' in response.data)
        self.assertTrue('updated_at' in response.data)
        self.assertTrue('items' in response.data)
        self.assertTrue('total_items' in response.data)
    
    def test_list_wishlist_items(self):
        """Test listing wishlist items"""
        # Create wishlist and add items
        wishlist = Wishlist.objects.create(customer=self.customer)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product2)
        
        # Make GET request
        response = self.client.get(self.wishlist_items_list_url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_add_item_to_wishlist(self):
        """Test adding an item to wishlist"""
        # Make POST request
        data = {'product_id': self.product1.id}
        response = self.client.post(self.wishlist_items_add_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify item was added
        wishlist = Wishlist.objects.get(customer=self.customer)
        self.assertEqual(wishlist.wishlist_items.count(), 1)
    
    def test_add_duplicate_item_to_wishlist(self):
        """Test adding a duplicate item to wishlist"""
        # Create wishlist and add product
        wishlist = Wishlist.objects.create(customer=self.customer)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Try to add same product again
        data = {'product_id': self.product1.id}
        response = self.client.post(self.wishlist_items_add_url, data)
        
        # Assert response (should fail)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no duplicate was added
        self.assertEqual(wishlist.wishlist_items.count(), 1)
    
    def test_remove_item_from_wishlist(self):
        """Test removing an item from wishlist"""
        # Create wishlist and add product
        wishlist = Wishlist.objects.create(customer=self.customer)
        item = WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Make DELETE request
        url = reverse('wishlist:wishlist-item-delete', args=[item.id])
        response = self.client.delete(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item was removed
        self.assertEqual(wishlist.wishlist_items.count(), 0)
    
    def test_retrieve_item_detail(self):
        """Test retrieving details of a specific wishlist item"""
        # Create wishlist and add product
        wishlist = Wishlist.objects.create(customer=self.customer)
        item = WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Make GET request
        url = reverse('wishlist:wishlist-item-detail', args=[item.id])
        response = self.client.get(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], item.id)
