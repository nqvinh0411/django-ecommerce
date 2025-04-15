from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_id', 'price', 'stock', 'created_at',)
    search_fields = ('name', 'category_id__name',)
    list_filter = ('category_id',)
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
