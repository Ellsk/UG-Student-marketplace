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
