from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_seller', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_seller', 'is_staff', 'is_superuser')


admin.site.register(User, CustomUserAdmin)
