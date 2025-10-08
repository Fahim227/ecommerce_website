from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Product, Category
from .forms import OrderForm
from django.core.paginator import Paginator

from django.db.models import Q


def home(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    categories = Category.objects.all()
    if query:
        products = products.filter(Q(title__icontains=query) | Q(short_description__icontains=query))
    return render(request, 'store/home.html', {'products': products, 'query': query,'categories':categories})


def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'store/categories.html', {'categories': categories})

def products_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    
    # Optional pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/products_by_category.html', {
        'category': category,
        'page_obj': page_obj,
    })



def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    gallery_images = product.images.all()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'gallery_images': gallery_images
    })

def all_products(request):
    products = Product.objects.all()  
    
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/all_products.html', {'page_obj': page_obj})


def order_create(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        print(request.POST) 
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            
            # Add success message
            messages.success(request, '✅ Your order has been confirmed! Thank you.')
            
            # Redirect to home page
            return redirect(reverse('store:home'))
        else:
            messages.error(request, '❌ There was an error with your order. Please check the details.')
    else:
        form = OrderForm()
    
    return render(request, 'store/order_form.html', {
        'form': form,
        'product': product,
    })