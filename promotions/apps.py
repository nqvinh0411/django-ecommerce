from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PromotionsConfig(AppConfig):
    name = 'promotions'
    verbose_name = _('Promotions')

    def ready(self):
        # Import signal handlers when app is ready
        try:
            import promotions.signals
        except ImportError:
            pass
