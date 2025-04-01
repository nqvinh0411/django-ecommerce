from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Warehouse, StockItem, StockMovement, InventoryAuditLog

User = get_user_model()

# Placeholder for actual tests
class WarehouseModelTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(
            name="Test Warehouse",
            location="Test Location",
            description="Test warehouse for unit tests",
            is_default=True,
            is_active=True
        )
    
    def test_warehouse_creation(self):
        """Test the basic creation of a warehouse"""
        self.assertEqual(self.warehouse.name, "Test Warehouse")
        self.assertEqual(self.warehouse.location, "Test Location")
        self.assertTrue(self.warehouse.is_default)
        self.assertTrue(self.warehouse.is_active)
        
    def test_warehouse_default_behavior(self):
        """Test that only one warehouse can be the default"""
        # Create second warehouse with is_default=True
        warehouse2 = Warehouse.objects.create(
            name="Second Warehouse",
            location="Second Location",
            description="Another test warehouse",
            is_default=True
        )
        
        # Refresh the first warehouse from the database
        self.warehouse.refresh_from_db()
        
        # Check that the first warehouse is no longer default
        self.assertFalse(self.warehouse.is_default)
        self.assertTrue(warehouse2.is_default)