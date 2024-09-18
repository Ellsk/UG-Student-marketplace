from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import CustomUser
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

# TUPLES
STATUS_CHOICE = [
    ("processing", "Processing"),
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
    cover_image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")  # Vendor's image
    #description = models.TextField(null=True, blank=True, default="I am an Amazing Vendor")
    description = RichTextUploadingField(null=True, blank=True, default="I am an Amazing Vendor")


    address = models.CharField(max_length=100, default="Legon Hall")
    contact = models.CharField(max_length=100, default="+233 (543) 789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Vendor linked to a CustomUser
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    #description = models.TextField(null=True, blank=True, default="This is a product")
    description = RichTextUploadingField(null=True, blank=True, default="This is a product")

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)  # Linked to a CustomUser
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")  # Linked to a Category
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="vendor")  # Linked to a Category

    # Allow for large max_digits to handle potentially expensive products
    price = models.DecimalField(max_digits=15, decimal_places=2, default="1.99")
    old_price = models.DecimalField(max_digits=15, decimal_places=2, default="2.99")

    specification = RichTextUploadingField(null=True, blank=True)
    #specification = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, default="Organic", null=True, blank=True)  
    stock_count = models.CharField(max_length=100, default="10", null=True, blank=True) 
    life = models.CharField(max_length=100, default="100 Days", null=True, blank=True) 
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True) 


    tags = TaggableManager(blank=True)
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
        discount_percentage = 100 - (self.price / self.old_price * 100)
        return discount_percentage

class ProductImages(models.Model):
    # Additional images for a product
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)  # Linked to a Product
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"  # Plural name in the admin section

######## Cart, Order, and OrderItems ########
class CartOrder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    coupons = models.ManyToManyField("api.Coupon", blank=True)
    
    shipping_method = models.CharField(max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)


    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    sku = ShortUUIDField(null=True, blank=True, length=5,prefix="SKU", max_length=20, alphabet="1234567890")
    oid = ShortUUIDField(null=True, blank=True, length=8, max_length=20, alphabet="1234567890")
    stripe_payment_intent = models.CharField(max_length=1000, null=True, blank=True)
    #date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    

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

    # def category_image(self):
    #     # Displays the category image in the admin interface
    #     return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def order_img(self):
        # Displays the order item image in the admin interface
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))

########## Product Review, Wishlist, Address ########

class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        # Check if the product is None to avoid AttributeError
        if self.product:
            return self.product.title
        else:
            return "No Product"  # Or any default string you prefer

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
    mobile = models.CharField(max_length=300, null=True)
    address = models.TextField()
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return self.address

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"
