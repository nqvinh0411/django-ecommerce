from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Import models - we'll need to use strings for some imports to avoid circular dependencies
from .models import Shipment, TrackingInfo


@receiver(post_save, sender='orders.Order')
def create_or_update_shipment_for_order(sender, instance, created, **kwargs):
    """
    Signal to automatically create a shipment when an order is created
    or update shipment status when order status changes.
    """
    Order = instance.__class__
    
    # If a new paid order is created, create a shipment
    if created and instance.status == 'PAID':
        # Find or create the default shipping method
        from .models import ShippingMethod
        default_method, _ = ShippingMethod.objects.get_or_create(
            name='Standard Shipping',
            defaults={
                'description': 'Default shipping method',
                'estimated_days': 5,
                'base_fee': 0.00,
                'is_active': True
            }
        )
        
        # Create a new shipment
        shipment = Shipment.objects.create(
            order=instance,
            shipping_method=default_method,
            shipment_status='PENDING',
            shipping_address=instance.shipping_address if hasattr(instance, 'shipping_address') else ''
        )
        
        # Create initial tracking info
        TrackingInfo.objects.create(
            shipment=shipment,
            status='ORDER_RECEIVED',
            location='Warehouse',
            note='Order received and ready for processing'
        )
    
    # If an existing order status changes to SHIPPED/DELIVERED, update the shipment
    elif not created:
        try:
            shipment = Shipment.objects.get(order=instance)
            
            if instance.status == 'SHIPPED' and shipment.shipment_status != 'SHIPPED':
                shipment.shipment_status = 'SHIPPED'
                shipment.shipped_at = timezone.now()
                shipment.save()
                
                TrackingInfo.objects.create(
                    shipment=shipment,
                    status='SHIPPED',
                    location='Warehouse',
                    note='Order has been shipped'
                )
                
            elif instance.status == 'DELIVERED' and shipment.shipment_status != 'DELIVERED':
                shipment.shipment_status = 'DELIVERED'
                shipment.delivered_at = timezone.now()
                shipment.save()
                
                TrackingInfo.objects.create(
                    shipment=shipment,
                    status='DELIVERED',
                    location='Destination',
                    note='Order has been delivered'
                )
                
            elif instance.status == 'CANCELLED' and shipment.shipment_status not in ['CANCELLED', 'DELIVERED']:
                shipment.shipment_status = 'CANCELLED'
                shipment.save()
                
                TrackingInfo.objects.create(
                    shipment=shipment,
                    status='CANCELLED',
                    location='N/A',
                    note='Order has been cancelled'
                )
                
        except Shipment.DoesNotExist:
            # If the order status changes to PAID but no shipment exists, create one
            if instance.status == 'PAID':
                create_or_update_shipment_for_order(sender, instance, created=True, **kwargs)


@receiver(post_save, sender=Shipment)
def update_order_status_on_shipment_change(sender, instance, created, **kwargs):
    """
    Signal to update order status when shipment status changes.
    This helps keep order and shipment statuses in sync.
    """
    # Avoid circular imports
    from django.apps import apps
    Order = apps.get_model('orders', 'Order')
    
    # Only proceed if we have an order and we're not in created mode
    # (to avoid infinite loops with the previous signal)
    if instance.order and not created:
        order = instance.order
        
        # Update order status based on shipment status
        if instance.shipment_status == 'SHIPPED' and order.status != 'SHIPPED':
            order.status = 'SHIPPED'
            order.save(update_fields=['status'])
            
        elif instance.shipment_status == 'DELIVERED' and order.status != 'DELIVERED':
            order.status = 'DELIVERED'
            order.save(update_fields=['status'])
            
        elif instance.shipment_status == 'CANCELLED' and order.status != 'CANCELLED':
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])


@receiver(post_save, sender=TrackingInfo)
def update_shipment_on_tracking_update(sender, instance, created, **kwargs):
    """
    Signal to update shipment status based on tracking updates.
    """
    if created and instance.shipment:
        shipment = instance.shipment
        tracking_status = instance.status.upper()
        
        # Update shipment based on tracking status
        if tracking_status == 'PICKED_UP' and shipment.shipment_status != 'SHIPPED':
            shipment.shipment_status = 'SHIPPED'
            shipment.shipped_at = instance.timestamp
            shipment.save(update_fields=['shipment_status', 'shipped_at'])
            
        elif tracking_status == 'DELIVERED' and shipment.shipment_status != 'DELIVERED':
            shipment.shipment_status = 'DELIVERED'
            shipment.delivered_at = instance.timestamp
            shipment.save(update_fields=['shipment_status', 'delivered_at'])