from django.contrib import admin
from .models import Category, Brand, Tag, Attribute, AttributeValue


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    prepopulated_fields = {'slug': ('value',)}


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_filterable', 'is_variant', 'created_at')
    list_filter = ('is_filterable', 'is_variant', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_filterable', 'is_variant')
    inlines = [AttributeValueInline]


class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'display_value', 'created_at')
    list_filter = ('attribute', 'created_at')
    search_fields = ('value', 'display_value')
    prepopulated_fields = {'slug': ('value',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)