from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    
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
    }