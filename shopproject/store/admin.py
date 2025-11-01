from django.contrib import admin
from .models import Product, Order, ProductImage, Category, OrderItem, StoreConfig


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    prepopulated_fields = {'name': ('id',)}


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'phone', 'address')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order' ]
