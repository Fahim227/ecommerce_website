from django.urls import path
from . import views


app_name = 'store'


urlpatterns = [
path('', views.home, name='home'),
path('product/<slug:slug>/', views.product_detail, name='product_detail'),
path('product/<slug:slug>/order/', views.order_create, name='order_create'),
]