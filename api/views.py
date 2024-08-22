from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from django.db.models import Avg, Count 
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from api.forms import ProductReviewForm
from django.template.loader import render_to_string

# Create your views here.

def index(request):
    #For displaying latest products
    #product = Product.objects.all().order_by("-id")
    
    product = Product.objects.filter(featured=True, product_status="published")
    
    context = {
        "products": product
    }
    
    return render(request, "core/index.html", context)

def product_list_view(request):
    #Whether the product is featured or not as long as it's published we will display
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
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(category=category, product_status="published") 
    
    context = {
        "category": category,
        "products": products
    }
    
    from django.http import HttpResponse

def index(request):
    #For displaying latest products
    #product = Product.objects.all().order_by("-id")
    
    product = Product.objects.filter(featured=True, product_status="published")
    
    context = {
        "products": product
    }
    
    return render(request, "core/index.html", context)

def product_list_view(request):
    #Whether the product is featured or not as long as it's published we will display
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
    category = Category.objects.get(cid=cid)
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
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published") 

    
    context = {
        "vendor": vendor,
        "products": products,
    }
    
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    # Getting all reviews related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # Getting average rating
    average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating']
    
    # Handling case where there are no reviews
    if average_rating is None:
        average_rating = 0
    
    #Product Review Form
    review_form = ProductReviewForm()

    #Checking to see if user already made a review
    make_review = True
    
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()
        
        if user_review_count > 0:
            make_review = False
            
    # Images
    p_image = product.p_images.all()
    
    context = {
        "product": product,
        "make_review": make_review,
        "review_form": review_form,
        "average_rating": round(average_rating, 1),  # Round to 1 decimal place
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
            review = ProductReview.objects.create(
                user=user,
                product=product,
                review=review_text,
                rating=rating,
            )

            average_rating = ProductReview.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating']
            if average_rating is None:
                average_rating = 0

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
    # Get the selected categories and vendors
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')
    
    
    #Fetching min and max prices
    min_price = request.GET['min_price']
    max_price = request.GET['max_price']
    
    # Start with all published products
    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    
    #Filtering the products based on min or max
    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)
    # Filter by categories if any are selected
    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()
    
    # Filter by vendors if any are selected
    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()  # Corrected from category to vendor
    
    # Render the filtered products to the template
    data = render_to_string('core/async/product-list.html', {'products': products})  # Corrected context
    
    return JsonResponse({'data': data})

def add_to_cart(request):
    cart_product = {}
    
    # Use 'id' as a string key to access the GET parameter
    product_id = request.GET.get('id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)
    
    title = request.GET.get('title')
    qty = request.GET.get('qty')
    price = request.GET.get('price')
    image = request.GET.get('image')
    pid = request.GET.get('pid')
    
    # Ensure that the required parameters are present
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
    
    # The cart data refers to the whole products added to cart
    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        
        # Checking if id already exists
        if product_id in cart_data:
            # Incrementing the existing product by updating the quantity
            cart_data[product_id]['qty'] += int(cart_product[product_id]['qty'])
        else:
            cart_data.update(cart_product)
        
        request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    
    # Calculate total cart items
    total_cart_items = sum(item['qty'] for item in request.session.get('cart_data_obj', {}).values())
    
    # Set the session as modified to ensure the changes are saved
    request.session.modified = True
    
    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': total_cart_items})
