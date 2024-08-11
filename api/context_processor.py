from api.models import Product, ProductImages, ProductReview, Wishlist, Address, CartOrder, Category, Vendor, CartOrderItems


def default(request):
    categories = Category.objects.all()
    return {
        'categories': categories,
    }