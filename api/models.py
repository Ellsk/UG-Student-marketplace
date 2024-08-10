from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import CustomUser

# TUPLES
STATUS_CHOICE = [
    ("process", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
]

STATUS = [
    ("draft", "Draft"),
    ("disable", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
]

RATING = [
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
]

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    # Category ID (cid) is auto-generated using ShortUUIDField with specific constraints
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcde12345")
    title = models.CharField(max_length=100, default="Food")  # Product Title
    image = models.ImageField(upload_to="category", default="category.jpg")  # Default image for category

    class Meta:
        verbose_name_plural = "Categories"  # Plural name in the admin section

    def category_image(self):
        # Displays the category image in the admin interface
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title  # Display title in the admin list view

class Tag(models.Model):
    pass  # Placeholder for Tag model implementation

class Vendor(models.Model):
    # Vendor ID (vid) is auto-generated using ShortUUIDField with specific constraints
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcde12345")
    title = models.CharField(max_length=100, default="Nestify")  # Vendor Name
    image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")  # Vendor's image
    description = models.TextField(null=True, blank=True, default="I am an Amazing Vendor")

    address = models.CharField(max_length=100, default="Legon Hall")
    contact = models.CharField(max_length=100, default="+233 (543) 789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    delivery_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Vendor linked to a CustomUser

    class Meta:
        verbose_name_plural = "Vendors"  # Plural name in the admin section

    def vendor_image(self):
        # Displays the vendor image in the admin interface
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title  # Display title in the admin list view

class Product(models.Model):
    # Product ID (pid) is auto-generated using ShortUUIDField with specific constraints
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="pd", alphabet="abcde12345")
    title = models.CharField(max_length=100, default="Nike")  # Product Title
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")  # Product image
    description = models.TextField(null=True, blank=True, default="This is a product")

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)  # Linked to a CustomUser
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Linked to a Category
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)  # Linked to a Category

    # Allow for large max_digits to handle potentially expensive products
    price = models.DecimalField(max_digits=15, decimal_places=2, default="1.99")
    old_price = models.DecimalField(max_digits=15, decimal_places=2, default="2.99")

    specification = models.TextField(null=True, blank=True)
    # tags = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)  # Linked to a Tag

    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)  # For digital products

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"  # Plural name in the admin section

    def product_image(self):
        # Displays the product image in the admin interface
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title  # Display title in the admin list view

    def get_percentage(self):
        # Calculate and return the percentage discount between old price and new price
        new_price = (self.price / self.old_price) * 100
        return new_price

class ProductImages(models.Model):
    # Additional images for a product
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  # Linked to a Product
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"  # Plural name in the admin section

######## Cart, Order, and OrderItems ########
class CartOrder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Linked to a CustomUser
    price = models.DecimalField(max_digits=15, decimal_places=2, default="1.99")
    paid_status = models.BooleanField(default=True)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Orders"  # Plural name in the admin section

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)  # Linked to a CartOrder
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2, default="1.99")
    total = models.DecimalField(max_digits=15, decimal_places=2, default="1.99")

    class Meta:
        verbose_name_plural = "Cart Order Items"  # Plural name in the admin section

    def order_img(self):
        # Displays the order item image in the admin interface
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))

########## Product Review, Wishlist, Address ########

class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    address = models.TextField()
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return self.address
