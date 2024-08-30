from api.models import Product, Category, Vendor, Address, Wishlist
from django.db.models import Min, Max
from django.contrib import messages


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    
    # Check if the user is authenticated before querying the address
    address = None
    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user)  # Use filter to allow for multiple addresses
    
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.filter(user=request.user)
        except:
            messages.warning(request, "You need to login before accessing your wishlist.")
            wishlist = 0
    else:
        wishlist = 0

    return {
        'categories': categories,
        'wishlist':wishlist,
        'address': address,
        'vendors': vendors,
        'min_max_price': min_max_price,
    }
