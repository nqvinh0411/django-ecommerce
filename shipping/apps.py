from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShippingConfig(AppConfig):
    name = 'shipping'
    verbose_name = _('Shipping')

    def ready(self):
        # Import signal handlers when app is ready
        import shipping.signals