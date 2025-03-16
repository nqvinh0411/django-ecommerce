from django.contrib import admin

from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_id', 'amount', 'status', 'created_at')
    search_fields = ('transaction_id',)
    list_filter = ('status',)


admin.site.register(Payment, PaymentAdmin)
