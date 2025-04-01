from django.test import TestCase
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product, Category
from wishlist.models import Wishlist, WishlistItem

User = get_user_model()


class WishlistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user and customer
        cls.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        cls.customer = Customer.objects.create(user=cls.user)
        
        # Create category and product
        cls.category = Category.objects.create(name='Test Category')
        cls.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=cls.category,
            seller_id=cls.user,
            stock=10
        )
        
        # Create wishlist and wishlist item
        cls.wishlist = Wishlist.objects.create(customer=cls.customer)
        cls.wishlist_item = WishlistItem.objects.create(
            wishlist=cls.wishlist,
            product=cls.product
        )

    def test_wishlist_creation(self):
        """Test that a wishlist can be created"""
        self.assertEqual(self.wishlist.customer, self.customer)
        self.assertIsNotNone(self.wishlist.created_at)
        self.assertEqual(str(self.wishlist), f"Wishlist of {self.user.email}")

    def test_wishlist_item_creation(self):
        """Test that a wishlist item can be created and linked to wishlist and product"""
        self.assertEqual(self.wishlist_item.wishlist, self.wishlist)
        self.assertEqual(self.wishlist_item.product, self.product)
        self.assertIsNotNone(self.wishlist_item.added_at)
        self.assertTrue(self.product.name in str(self.wishlist_item))

    def test_customer_wishlist_relationship(self):
        """Test the relationship between customer and wishlist"""
        # A customer should have one wishlist
        self.assertEqual(self.customer.wishlist, self.wishlist)
        
    def test_wishlist_item_unique_constraint(self):
        """Test that a product can only be added once to a wishlist"""
        # Adding the same product again should raise an IntegrityError
        with self.assertRaises(Exception):
            WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product
            )
    
    def test_wishlist_items_ordering(self):
        """Test that wishlist items are ordered by added_at in descending order"""
        # Create a new product and add it to the wishlist
        product2 = Product.objects.create(
            name='Test Product 2',
            description='Test Description 2',
            price=199.99,
            category=self.category,
            seller_id=self.user,
            stock=5
        )
        
        item2 = WishlistItem.objects.create(
            wishlist=self.wishlist,
            product=product2
        )
        
        # Get all items in the wishlist
        items = WishlistItem.objects.filter(wishlist=self.wishlist)
        
        # The newest item should be first
        self.assertEqual(items[0], item2)
        self.assertEqual(items[1], self.wishlist_item)
