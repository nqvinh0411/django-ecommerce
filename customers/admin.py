from django.contrib import admin
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity

@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_rate', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'group', 'loyalty_points', 'created_at']
    list_filter = ['group', 'gender', 'created_at']
    search_fields = ['user__email', 'phone_number', 'notes']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_type', 'is_default', 'city', 'country']
    list_filter = ['address_type', 'is_default', 'city', 'country', 'created_at']
    search_fields = ['customer__user__email', 'street_address', 'city', 'country']
    raw_id_fields = ['customer']

@admin.register(CustomerActivity)
class CustomerActivityAdmin(admin.ModelAdmin):
    list_display = ['customer', 'activity_type', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['customer__user__email', 'activity_type', 'ip_address']
    readonly_fields = ['created_at']
    raw_id_fields = ['customer']
