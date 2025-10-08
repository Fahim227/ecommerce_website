from django.contrib import admin
from .models import Product, Order, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'full_name', 'email', 'phone', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'phone', 'address')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
