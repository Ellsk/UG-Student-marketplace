from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from django.db.models import Avg, Count 
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from api.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

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
