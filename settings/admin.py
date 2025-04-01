from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import StoreSetting, Currency, LanguageSetting, EmailTemplate


class StoreSettingAdmin(admin.ModelAdmin):
    """
    Admin configuration for StoreSetting model.
    Ensures only one instance can exist.
    """
    list_display = ('store_name', 'support_email', 'default_currency', 'default_language', 'is_maintenance_mode', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Store Information'), {
            'fields': ('store_name', 'store_logo', 'support_email', 'phone_number', 'address')
        }),
        (_('Defaults'), {
            'fields': ('default_currency', 'default_language')
        }),
        (_('Status'), {
            'fields': ('is_maintenance_mode',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """
        Check if adding StoreSetting is allowed.
        Only allow adding if no instance exists yet.
        """
        return not StoreSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of StoreSetting.
        """
        return False


class CurrencyAdmin(admin.ModelAdmin):
    """
    Admin configuration for Currency model.
    """
    list_display = ('code', 'name', 'symbol', 'exchange_rate_to_base', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')
    search_fields = ('code', 'name')
    fieldsets = (
        (_('Currency Information'), {
            'fields': ('code', 'name', 'symbol')
        }),
        (_('Exchange Rate'), {
            'fields': ('exchange_rate_to_base',)
        }),
        (_('Status'), {
            'fields': ('is_default', 'is_active')
        }),
    )


class LanguageSettingAdmin(admin.ModelAdmin):
    """
    Admin configuration for LanguageSetting model.
    """
    list_display = ('code', 'name', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')
    search_fields = ('code', 'name')
    fieldsets = (
        (_('Language Information'), {
            'fields': ('code', 'name')
        }),
        (_('Status'), {
            'fields': ('is_default', 'is_active')
        }),
    )


class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmailTemplate model.
    """
    list_display = ('template_key', 'subject', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('template_key', 'subject', 'body_html', 'body_text')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Template Information'), {
            'fields': ('template_key', 'subject')
        }),
        (_('Content'), {
            'fields': ('body_html', 'body_text')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Register the models with their admin classes
admin.site.register(StoreSetting, StoreSettingAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(LanguageSetting, LanguageSettingAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
