from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkflowConfig(AppConfig):
    name = 'workflow'
    verbose_name = _('Workflow Management')
    
    def ready(self):
        """
        Import signals when the app is ready.
        This is where you can register any signal handlers for the workflow app.
        """
        try:
            import workflow.signals  # noqa
        except ImportError:
            pass
