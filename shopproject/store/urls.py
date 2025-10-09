from django.urls import path
from . import views


app_name = 'store'


urlpatterns = [
path('', views.home, name='home'),
path('product/<slug:slug>/', views.product_detail, name='product_detail'),
path('product/<slug:slug>/order/', views.order_create, name='order_create'),

    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('order/success/', views.order_success, name='order_success'),

path('products', views.all_products, name='products'),
path('categories/', views.categories_list, name='categories_list'),
path('category/<slug:slug>/', views.products_by_category, name='products_by_category'),
    
]