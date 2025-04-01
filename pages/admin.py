from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Page, Banner, MenuItem


class MenuItemInline(admin.TabularInline):
    """
    Inline admin for child menu items.
    """
    model = MenuItem
    extra = 1
    fk_name = 'parent'
    fields = ('label', 'url', 'order', 'is_active')
    ordering = ('order',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Admin configuration for Page model.
    """
    list_display = ('title', 'slug', 'is_published', 'published_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('title', 'slug', 'content_html', 'content_text')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'content_preview')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'is_published', 'published_at')
        }),
        (_('Content'), {
            'fields': ('content_html', 'content_preview', 'content_text')
        }),
        (_('SEO Settings'), {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """
        Display a preview of the HTML content.
        """
        if obj.content_html:
            return format_html(
                '<div style="max-width: 800px; max-height: 300px; overflow: auto; '
                'padding: 10px; border: 1px solid #ddd;">{}</div>',
                obj.content_html
            )
        return _('No content to preview')
    content_preview.short_description = _('Content Preview')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Banner model.
    """
    list_display = ('title', 'position', 'is_active', 'start_date', 'end_date', 'image_preview')
    list_filter = ('position', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'link_url')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        (_('Banner Information'), {
            'fields': ('title', 'image', 'image_preview', 'link_url')
        }),
        (_('Display Settings'), {
            'fields': ('position', 'is_active', 'start_date', 'end_date')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """
        Display a thumbnail preview of the banner image.
        """
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 100px;" /></a>',
                obj.image.url, obj.image.url
            )
        return _('No image to preview')
    image_preview.short_description = _('Image Preview')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for MenuItem model.
    """
    list_display = ('label', 'url', 'menu_type', 'parent', 'order', 'is_active')
    list_filter = ('menu_type', 'is_active')
    search_fields = ('label', 'url')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MenuItemInline]
    
    fieldsets = (
        (_('Menu Item Information'), {
            'fields': ('label', 'url', 'order')
        }),
        (_('Hierarchical Settings'), {
            'fields': ('parent', 'menu_type')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Only show root menu items in the list view.
        Child items are managed through the inline admin.
        """
        qs = super().get_queryset(request)
        if not request.path.endswith('/change/'):
            qs = qs.filter(parent__isnull=True)
        return qs
