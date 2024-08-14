from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from taggit.models import Tag
from django.db.models import Avg, Count 
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from api.forms import ProductReviewForm
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
from django.shortcuts import render
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
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
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    #Getting all review related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    
    #Getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    #Images
    p_image = product.p_images.all()
    
    context = {
        "product": product,
        "average_rating": average_rating,
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