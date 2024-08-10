from django.http import HttpResponse
from django.shortcuts import render
from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
# Create your views here.

def index(request):
    product = Product.objects.all()
    
    context = {
        "products": product
    }
    
    return render(request, "core/index.html", context)
