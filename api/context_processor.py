from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems
from django.db.models import Count, Min, Max

def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    
    # Check if the user is authenticated before querying the address
    address = None
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
        except Address.DoesNotExist:
            address = None
    
    return {
        'categories': categories,
        'address': address,
        'vendors': vendors,
        'min_max_price': min_max_price,
    }