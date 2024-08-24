from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from django.db.models import Avg, Count 
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from api.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

# Create your views here.

def index(request):
    product = Product.objects.filter(featured=True, product_status="published")
    context = {
        "products": product
    }
    return render(request, "core/index.html", context)

def product_list_view(request):
    product = Product.objects.filter(product_status="published")
    context = {
        "products": product
    }
    return render(request, "core/product-list.html", context)

def category_list_view(request):    
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(request, "core/category-list.html", context)

def category_product_list_view(request, cid):
    category = get_object_or_404(Category, cid=cid)
    products = Product.objects.filter(category=category, product_status="published")
    context = {
        "category": category,
        "products": products
    }
    return render(request, "core/category-product-list.html", context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors": vendors,
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = get_object_or_404(Vendor, vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {
        "vendor": vendor,
        "products": products,
    }
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating'] or 0
    
    review_form = ProductReviewForm()
    make_review = True
    
    if request.user.is_authenticated:
        if ProductReview.objects.filter(user=request.user, product=product).exists():
            make_review = False
            
    p_image = product.p_images.all()
    
    context = {
        "product": product,
        "make_review": make_review,
        "review_form": review_form,
        "average_rating": round(average_rating, 1),
        "reviews": reviews,
        "products": products,
        "p_image": p_image,
    }
    return render(request, "core/product-detail.html", context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
    context = {
        "products": products,
        "tag": tag,
    }
    return render(request, "core/tag.html", context)

def ajax_add_review(request, pid):
    product = get_object_or_404(Product, pk=pid)
    user = request.user

    if request.method == "POST":
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        if review_text and rating:
            try:
                rating = float(rating)
            except ValueError:
                return JsonResponse({'bool': False, 'error': 'Invalid rating value'}, status=400)

            review = ProductReview.objects.create(
                user=user,
                product=product,
                review=review_text,
                rating=rating,
            )

            average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating'] or 0

            return JsonResponse({
                'bool': True,
                'context': {
                    'user': user.id,
                    'review': review_text,
                    'rating': rating,
                },
                'average_rating': round(average_rating, 1),
            })

        return JsonResponse({'bool': False, 'error': 'Invalid data'}, status=400)

    return JsonResponse({'bool': False, 'error': 'Invalid method'}, status=405)

def search_view(request):
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query).order_by("-date")
    context = {
        "products": products,
        'query': query,
    }
    return render(request, "core/search.html", context)

def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000000)  # Set a reasonable default if not provided
    
    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if categories:
        products = products.filter(category__id__in=categories).distinct()
    
    if vendors:
        products = products.filter(vendor__id__in=vendors).distinct()
    
    data = render_to_string('core/async/product-list.html', {'products': products})
    return JsonResponse({'data': data})

def add_to_cart(request):
    cart_product = {}
    
    product_id = request.GET.get('id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)
    
    title = request.GET.get('title')
    qty = request.GET.get('qty')
    price = request.GET.get('price')
    image = request.GET.get('image')
    pid = request.GET.get('pid')
    
    if not all([title, qty, price, image, pid]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        price = float(price)
    except ValueError:
        return JsonResponse({'error': 'Invalid price format'}, status=400)
    
    cart_product[product_id] = {
        'title': title,
        'qty': int(qty),
        'price': price,
        'image': image,
        'pid': pid,
    }
    
    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            cart_data[product_id]['qty'] += int(cart_product[product_id]['qty'])
        else:
            cart_data.update(cart_product)
        request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    
    total_cart_items = sum(item['qty'] for item in request.session.get('cart_data_obj', {}).values())
    request.session.modified = True
    
    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': total_cart_items})

def cart_view(request):
    cart_total_amount = 0
    total_cart_items = sum(item['qty'] for item in request.session.get('cart_data_obj', {}).values())

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': total_cart_items, 'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request,"Your cart is empty")
        return render(request, "core/cart.html", {"cart_data": "", 'totalcartitems': total_cart_items, 'cart_total_amount': cart_total_amount})

def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
            
    cart_total_amount = 0
    total_cart_items = sum(item['qty'] for item in request.session.get('cart_data_obj', {}).values())

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': total_cart_items, 'cart_total_amount': cart_total_amount})

def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).order_by("-id")
    context = {"wishlist": wishlist}
    return render(request, "core/wishlist.html", context)

def ajax_add_to_wishlist(request):
    pid = request.GET.get("product")
    product = Product.objects.get(pid=pid)
    check_wishlist = Wishlist.objects.filter(product=product, user=request.user).count()
    if check_wishlist > 0:
        return JsonResponse({"bool": False})
    else:
        wishlist = Wishlist.objects.create(product=product, user=request.user)
        return JsonResponse({"bool": True})

def delete_item_from_wishlist(request):
    product_id = request.GET.get("id")
    Wishlist.objects.filter(product_id=product_id, user=request.user).delete()
    wishlist = Wishlist.objects.filter(user=request.user).order_by("-id")
    context = {"wishlist": wishlist}
    return render(request, "core/ajax-wishlist.html", context)

def search_address(request):
    if 'term' in request.GET:
        qs = Address.objects.filter(name__icontains=request.GET.get('term'))
        titles = list()
        for address in qs:
            titles.append(address.name)
        return JsonResponse(titles, safe=False)

