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


# store/views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # optional if you’re handling CSRF manually in JS (but you already do)
def cart_checkout(request):
    if request.method == 'POST':
        cart_json = request.POST.get('cart_json')
        if not cart_json:
            return redirect('store:order_success')  # fallback if empty cart

        try:
            cart_data = json.loads(cart_json)
        except json.JSONDecodeError:
            cart_data = {}


        # 🧩 Example: pass cart to order form template
        return render(request, 'store/order_form.html', {
            'cart_items': cart_data,
        })

    # Add success message
    messages.success(request, '✅ Your order has been confirmed! Thank you.')
    # Redirect to success page
    return redirect('store:order_success')
    


import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from .forms import OrderForm

def order_create(request, slug=None):
    """
    Handles both:
    - Buy Now (single product via slug)
    - Cart Checkout (multiple products via POST cart_json)
    """
    cart_items = {}

    if request.method == "POST":
        form = OrderForm(request.POST)
        cart_json = request.POST.get("cart_json")
        if form.is_valid():
            order = form.save()
            
            # Process cart items if sent
            if cart_json:
                try:
                    cart_items_data = json.loads(cart_json)
                except json.JSONDecodeError:
                    cart_items_data = {}

                for slug, item in cart_items_data.items():
                    product = Product.objects.get(slug=slug)
                    quantity = int(item["quantity"])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

            # Process single Buy Now product if slug provided and no cart
            elif slug:
                product = get_object_or_404(Product, slug=slug)
                quantity = int(request.POST.get("quantity", 1))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            # Add success message
            messages.success(request, '✅ Your order has been confirmed! Thank you.')
            # Redirect to success page
            return redirect('store:order_success')
        else:
            messages.error(request, '❌ There was an error with your order. Please check the details.')
    else:
        form = OrderForm()
        # Prepare cart_items for template display
        if slug and not request.GET.get("cart_checkout"):
            product = get_object_or_404(Product, slug=slug)
            cart_items = {
                product.slug: {
                    "name": product.title,
                    "price": float(product.price),
                    "quantity": 1,
                    "image": product.image.url if product.image else ""
                }
            }

    return render(request, "store/order_form.html", {
        "form": form,
        "cart_items": cart_items
    })


# def order_create(request, slug):
#     product = get_object_or_404(Product, slug=slug)
    
#     if request.method == 'POST':
#         print(request.POST) 
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.product = product
#             order.save()
            
#             # Add success message
#             messages.success(request, '✅ Your order has been confirmed! Thank you.')
            
#             # Redirect to home page
#             return redirect(reverse('store:home'))
#         else:
#             messages.error(request, '❌ There was an error with your order. Please check the details.')
#     else:
#         form = OrderForm()
    
#     return render(request, 'store/order_form.html', {
#         'form': form,
#         'product': product,
#     })

def order_success(request):
    return render(request, "store/order_success.html")