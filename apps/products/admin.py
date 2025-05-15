from django.contrib import admin
from .models import Product, ProductOption

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'additional_price', 'stock')
    list_filter = ('product', 'color', 'size')
    search_fields = ('product__name', 'color', 'size')
    ordering = ('product', 'color', 'size')
