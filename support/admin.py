from django.contrib import admin
from .models import SupportCategory, SupportTicket, TicketReply, FAQ


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'customer', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('subject', 'customer__user__email', 'customer__user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TicketReplyInline]
    date_hierarchy = 'created_at'


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'is_staff_reply', 'created_at')
    list_filter = ('is_staff_reply', 'created_at')
    search_fields = ('ticket__subject', 'user__email', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published')
    list_filter = ('is_published', 'category')
    search_fields = ('question', 'answer')
    fieldsets = (
        (None, {
            'fields': ('question', 'answer')
        }),
        ('Publishing options', {
            'fields': ('category', 'is_published')
        }),
    )
