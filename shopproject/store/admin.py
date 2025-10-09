from django.contrib import admin
from .models import Product, Order, ProductImage, Category


@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'name': ('slug',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'phone', 'address')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
