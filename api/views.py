
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from django.db.models import Avg, Count 
from api.models import Coupon, Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from api.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from userauths.models import ContactUs, Profile


from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required

#payment integration
import stripe
from paypal.standard.forms import PayPalPaymentsForm
from django.core import serializers

import calendar
from django.db.models.functions import ExtractMonth



# Index view for displaying latest products
def index(request):
    products = Product.objects.filter(featured=True, product_status="published")
    context = {"products": products}
    return render(request, "core/index.html", context)

# View to list all published products
def product_list_view(request):
    products = Product.objects.filter(product_status="published")
    context = {"products": products}
    return render(request, "core/product-list.html", context)

# View to list all categories
def category_list_view(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "core/category-list.html", context)

# View to list products in a specific category
def category_product_list_view(request, cid):
    category = get_object_or_404(Category, cid=cid)
    products = Product.objects.filter(category=category, product_status="published")
    context = {"category": category, "products": products}
    return render(request, "core/category-product-list.html", context)

# View to list all vendors
def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {"vendors": vendors}
    return render(request, "core/vendor-list.html", context)

# View to show details of a specific vendor and their products
def vendor_detail_view(request, vid):
    vendor = get_object_or_404(Vendor, vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {"vendor": vendor, "products": products}
    return render(request, "core/vendor-detail.html", context)

# View to show details of a specific product and related products
def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)
    related_products = Product.objects.filter(category=product.category, product_status="published").exclude(pid=pid)
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating'] or 0
    review_form = ProductReviewForm()
    make_review = request.user.is_authenticated and not ProductReview.objects.filter(user=request.user, product=product).exists()
    p_images = product.p_images.all()

    context = {
        "product": product,
        "make_review": make_review,
        "review_form": review_form,
        "average_rating": round(average_rating, 1),
        "reviews": reviews,
        "products": related_products,
        "p_images": p_images,
    }
    return render(request, "core/product-detail.html", context)

# View to list products based on tags
def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {"products": products, "tag": tag}
    return render(request, "core/tag.html", context)

# AJAX view to add a review
def ajax_add_review(request, pid):
    product = get_object_or_404(Product, pk=pid)
    if request.method == "POST":
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        if review_text and rating:
            review = ProductReview.objects.create(
                user=request.user,
                product=product,
                review=review_text,
                rating=rating,
            )
            average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating'] or 0
            return JsonResponse({
                'bool': True,
                'context': {
                    'user': request.user.id,
                    'review': review_text,
                    'rating': rating,
                },
                'average_rating': round(average_rating, 1),
            })

        return JsonResponse({'bool': False, 'error': 'Invalid data'}, status=400)

    return JsonResponse({'bool': False, 'error': 'Invalid method'}, status=405)

# Search view
def search_view(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(title__icontains=query).order_by("-date")
    context = {"products": products, 'query': query}
    return render(request, "core/search.html", context)

# View to filter products by category, vendor, and price
def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000000)

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    products = products.filter(price__gte=min_price, price__lte=max_price)

    if categories:
        products = products.filter(category__id__in=categories).distinct()
    if vendors:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string('core/async/product-list.html', {'products': products})
    return JsonResponse({'data': data})

# View to add a product to the cart
def add_to_cart(request):
    product_id = request.GET.get('id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)

    title = request.GET.get('title')
    qty = request.GET.get('qty', 1)
    price = request.GET.get('price')
    image = request.GET.get('image')
    pid = request.GET.get('pid')

    if not all([title, price, image, pid]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        qty = int(qty)
        price = float(price)
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity or price format'}, status=400)

    cart_product = {
        product_id: {
            'title': title,
            'qty': qty,
            'price': price,
            'image': image,
            'pid': pid,
        }
    }

    cart_data = request.session.get('cart_data_obj', {})
    if product_id in cart_data:
        cart_data[product_id]['qty'] += qty
    else:
        cart_data.update(cart_product)

    request.session['cart_data_obj'] = cart_data
    request.session.modified = True

    total_cart_items = sum(int(item['qty']) for item in request.session.get('cart_data_obj', {}).values())
    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': total_cart_items})

# View to display the cart and recalculate the total price
def cart_view(request):
    cart_total_amount = 0.0
    total_cart_items = 0
    cart_data = request.session.get('cart_data_obj', {})

    for item in cart_data.values():
        cart_total_amount += int(item['qty']) * float(item['price'])
        total_cart_items += int(item['qty'])

    if not cart_data:
        messages.warning(request, "Your cart is empty")

    context = {
        "cart_data": cart_data,
        'totalcartitems': total_cart_items,
        'cart_total_amount': cart_total_amount,
    }
    return render(request, "core/cart.html", context)

# View to delete an item from the cart
def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))
    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            del cart_data[product_id]
            request.session['cart_data_obj'] = cart_data
            request.session.modified = True

    total_cart_items = sum(item['qty'] for item in cart_data.values())
    cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in cart_data.values())

    context = render_to_string('core/async/cart-list.html', {
        "cart_data": cart_data, 
        'totalcartitems': total_cart_items, 
        'cart_total_amount': cart_total_amount
    })
    return JsonResponse({"data": context, 'totalcartitems': total_cart_items})

def update_cart(request):
    product_id = str(request.GET.get('id'))
    product_qty = request.GET.get('qty')
    
    # Debugging print statements
    print(f"Received product_id: {product_id}")
    print(f"Received product_qty: {product_qty}")
    
    if not product_qty or not product_qty.isdigit():
        print("Invalid quantity received.")
        return JsonResponse({"error": "Invalid quantity"}, status=400)
    
    product_qty = int(product_qty)

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            cart_data[product_id]['qty'] = product_qty
            request.session.modified = True

            total_cart_items = sum(int(item.get('qty', 0)) for item in cart_data.values())
            cart_total_amount = sum(int(item.get('qty', 0)) * float(item.get('price', 0.0)) for item in cart_data.values())

            context = render_to_string('core/async/cart-list.html', {
                "cart_data": cart_data, 
                'totalcartitems': total_cart_items, 
                'cart_total_amount': cart_total_amount
            })

            return JsonResponse({"cart_html": context, 'totalcartitems': total_cart_items})
        
    return JsonResponse({"error": "Product not found in cart"}, status=404)

@login_required
def save_checkout_info(request):
    cart_total_amount = 0
    total_amount = 0
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        # Store user info in the session
        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country

        if 'cart_data_obj' in request.session:
            # Calculate total amount
            for p_id, item in request.session['cart_data_obj'].items():
                total_amount += int(item['qty']) * float(item['price'])

            # Create Order Object
            order = CartOrder.objects.create(
                user=request.user,
                price=total_amount,
                full_name=request.session['full_name'],
                email=request.session['email'],
                phone=request.session['mobile'],
                address=request.session['address'],
                city=request.session['city'],
                state=request.session['state'],
                country=request.session['country'],
            )

            # Clean up session data
            for key in ['full_name', 'email', 'mobile', 'address', 'city', 'state', 'country']:
                if key in request.session:
                    del request.session[key]

            # Create CartOrderItems
            for p_id, item in request.session['cart_data_obj'].items():
                CartOrderItems.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO-" + str(order.id),
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price']),
                )

        return redirect("api:checkout", order.oid)

    return redirect("api:checkout")

@login_required
def checkout(request, oid):
    try:
        order = CartOrder.objects.get(oid=oid)
        order_items = CartOrderItems.objects.filter(order=order)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('api:cart')

    if request.method == "POST":
        code = request.POST.get("code")
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            #After coupon activation we apply a security mechanism to check if it has been applied to an order before
            if coupon in order.coupons.all():
                messages.warning(request, "Coupon already activated")
            else:
                discount = order.price * coupon.discount / 100 
                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()
                messages.success(request, "Coupon Activated")
        else:
            messages.error(request, "Coupon does not exist.")

        return redirect("api:checkout", order.oid)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "core/checkout.html", context)

@csrf_exempt
def create_checkout_session(request, oid):
    order = CartOrder.objects.get(oid=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid]))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})





@login_required
def payment_completed_view(request):
    order = CartOrder.objects.get(oid=oid)
    
    if order.paid_status == False:
        order.paid_status = True
        order.save()
        
    context = {
        "order": order,
        #"stripe_publishable_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'core/payment-completed.html', context)

@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)
    
    orders = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
    month = []
    total_orders = []

    for i in orders:
        #Calender will change the number to exactly month name
        month.append(calendar.month_name[i["month"]])
        total_orders.append(i["count"])


    if request.method == "POST":
        address_text = request.POST.get("address")
        phone = request.POST.get("phone")

        # Check if the same address already exists for the user
        existing_address = Address.objects.filter(user=request.user, address=address_text, mobile=phone).first()

        if not existing_address:
            # If the address doesn't exist, create a new one
            Address.objects.create(
                user=request.user,
                address=address_text,
                mobile=phone,
            )
            messages.success(request, "Address added successfully.")
        else:
            messages.info(request, "This address already exists.")

        return redirect("api:dashboard")

    user_profile = Profile.objects.get(user=request.user)
    print("user profile is: ####",  user_profile)

    context = {
        'user_profile': user_profile,
        'orders': orders,
        'orders_list': orders_list,
        'address': address,
        'month': month,
        'total_orders': total_orders,

    }
    return render(request, 'core/dashboard.html', context)

def order_detail(request, id):
    # Retrieve the order based on the user and the order ID
    order = get_object_or_404(CartOrder, user=request.user, id=id)
    # Retrieve the items associated with the order
    order_items = CartOrderItems.objects.filter(order=order)

    context = {
        "order": order,  # Pass the order to the template if needed
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)

def make_address_default(request):
    id = request.GET.get('id')
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.all()
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)


    # w

def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id is:" + product_id)

    context = {}

    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = Wishlist.objects.create(
            user=request.user,
            product=product,
        )
        context = {
            "bool": True
        }

    return JsonResponse(context)

def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = Wishlist.objects.filter(user=request.user)
    wishlist_d = Wishlist.objects.get(id=pid)
    delete_product = wishlist_d.delete()
    
    context = {
        "bool":True,
        "w":wishlist
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('core/async/wishlist-list.html', context)
    return JsonResponse({'data':t,'w':wishlist_json})

# Links to Other Pages Section
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})


def about_us(request):
    return render(request, "core/about_us.html")


def purchase_guide(request):
    return render(request, "core/purchase_guide.html")

def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

def terms_of_service(request):
    return render(request, "core/terms_of_service.html")


