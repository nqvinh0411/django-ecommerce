from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

# Dynamically import these models to avoid circular imports
try:
    from products.models import Product
    from .models import StockItem, Warehouse, InventoryAuditLog

    @receiver(post_save, sender=Product)
    def create_stock_item_for_new_product(sender, instance, created, **kwargs):
        """
        Automatically create a stock item entry for each new product in the default warehouse.
        """
        if created:
            try:
                # Get the default warehouse
                default_warehouse = Warehouse.objects.filter(is_default=True).first()
                
                # If there's no default warehouse yet, create one
                if not default_warehouse:
                    default_warehouse = Warehouse.objects.create(
                        name="Main Warehouse",
                        location="Default Location",
                        description="Default warehouse created automatically",
                        is_default=True,
                        is_active=True
                    )
                
                # Create a stock item with 0 quantity
                with transaction.atomic():
                    stock_item = StockItem.objects.create(
                        product=instance,
                        warehouse=default_warehouse,
                        quantity=0,
                        low_stock_threshold=5,
                        is_tracked=True
                    )
                    
                    # Create an audit log entry for the new stock item
                    system_user = User.objects.filter(is_superuser=True).first()
                    InventoryAuditLog.objects.create(
                        stock_item=stock_item,
                        change_type='SYSTEM',
                        changed_by=system_user,
                        old_quantity=0,
                        new_quantity=0,
                        note="Initial stock item created for new product"
                    )
            except Exception as e:
                # Log error, but don't block product creation
                print(f"Error creating stock item for product {instance}: {str(e)}")
except ImportError:
    # Silently pass if Product model doesn't exist yet (during migrations)
    pass