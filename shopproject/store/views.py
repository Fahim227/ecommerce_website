from django.contrib import messages
from .models import Product, Category
from .forms import OrderForm
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, OrderItem

import json
from .forms import OrderForm


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



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    gallery_images = product.images.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)
    
    paginator = Paginator(related_products, 100)
    page_number = request.GET.get('page')
    related_products_page = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('store/_store_product_card.html', {
            'related_products': related_products_page
        }, request=request)
        return JsonResponse({'html': html})

    return render(request, 'store/product_detail.html', {
        'product': product,
        'gallery_images': gallery_images[:5],
        'related_products': related_products_page
    })

def all_products(request):
    products = Product.objects.all()  
    
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/all_products.html', {'page_obj': page_obj})


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
    

def order_create(request, id=None):

    """
    Handles:
    - Buy Now (single product via id)
    - Cart Checkout (multiple products via POST cart_json)
    """
    cart_items = {}

    if request.method == "POST":
        form = OrderForm(request.POST)
        cart_json = request.POST.get("cart_json")
        print("cart_items",request.POST.get("cart_items"))

        if form.is_valid():
            order = form.save(commit=False)

            # -------------------------------
            # 🧮 Calculate subtotal
            # -------------------------------
            subtotal = 0
            cart_items_data = {}

            if cart_json:
                try:
                    cart_items_data = json.loads(cart_json)
                except json.JSONDecodeError:
                    cart_items_data = {}
                print("cart_items_data",cart_items_data)
                for pid, item in cart_items_data.items():
                    try:
                        product = Product.objects.get(id=pid)
                        subtotal += float(product.price) * int(item["quantity"])
                    except Product.DoesNotExist:
                        continue

            elif id:  # Single "Buy Now" case
                product = get_object_or_404(Product, id=id)
                quantity = int(request.POST.get("quantity", 1))
                subtotal += float(product.price) * quantity
                print("Buy Now")
            # -------------------------------
            # 🚚 Shipping logic based on district
            # -------------------------------
            district = form.cleaned_data.get("district", "").lower()
            if district == "dhaka":
                shipping_charge = 80
            else:
                shipping_charge = 150

            # -------------------------------
            # 💰 Final total
            # -------------------------------
            total = subtotal + shipping_charge

            # -------------------------------
            # Save order with calculated values
            # -------------------------------
            print("subtotal",subtotal)
            print("total",total)
            order.subtotal = subtotal
            order.shipping_charge = shipping_charge
            order.total = total
            order.save()

            # -------------------------------
            # Save order items
            # -------------------------------
            if cart_json:
                for pid, item in cart_items_data.items():
                    try:
                        product = Product.objects.get(id=pid)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=int(item["quantity"]),
                            price=product.price
                        )
                    except Product.DoesNotExist:
                        continue
            elif id:
                product = get_object_or_404(Product, id=id)
                quantity = int(request.POST.get("quantity", 1))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            messages.success(request, "✅ Your order has been confirmed! Thank you.")
            return redirect("store:order_success")

        else:
            messages.error(request, "❌ There was an error with your order. Please check the details.")
    else:
        form = OrderForm()

        # 🛒 Prepare single product preview if direct buy
        if id and not request.GET.get("cart_checkout"):
            product = get_object_or_404(Product, id=id)
            cart_items = {
                product.id: {
                    "name": product.title,
                    "price": float(product.price),
                    "quantity": 1,
                    "image": product.image.url if product.image else "",
                }
            }
        else:
            cart_json = request.GET.get('cart_json')
           

            try:
                cart_items = json.loads(cart_json)
            except json.JSONDecodeError:
                cart_items = {}

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