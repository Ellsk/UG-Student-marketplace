from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import CustomUser

#TUPLES
STATUS_CHOICE = {
    {"process", "Processing"},
    {"shipped", "Shipped"},
    {"delivered", "Delivered"},
}

STATUS = {
    {"draft", "Draft"},
    {"disable", "Disabled"},
    {"rejected", "Rejected"},
    {"in_review", "in Review"},
    {"publish", "Published"},
} 

RATING = {
    {1, "★☆☆☆☆"},
    {2, "★★☆☆☆"},
    {3, "★★★☆☆"},
    {4, "★★★★☆"},
    {5, "★★★★★"},
}

def user_directory_path(instance, filename):
    return 'user_(0)/(1)'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcde12345") #cat simply means category
    title = models.CharField(max_length=100, default="Food") #Product Title
    image = models.ImageField(upload_to="category", default="category.jpg")
    
    class Meta:
        verbose_name_plural ="Categories" #For Plural change in admin section
        
    def category_image(self):
        return mark_safe('<img scr="%s" width="50" height="50" />' %(self.image.url))
    
    def __str__(self):
        return self.title
    #Since the cid is calculated automatically we return only title and image scr
class Tag(models.Model):
    pass

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcde12345") #ven simply means vendor
    
    title = models.CharField(max_length=100, default="Nestify") #Vendor Product Title
    image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg") # Instead of uploading to separate image product file lets relate each vendor with his own product upload path
    description = models.TextField(null=True, blank=True, default="I am an Amazing Vendor")
    
    address = models.CharField(max_length=100, default="Legon Hall")
    contact = models.CharField(max_length=100, default="+233 (543) 789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    delivery_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) #CASCADE to delete vendor as well as their product, you can user SETNULL if you want to maintain product but delete vendor
    
    class Meta:
        verbose_name_plural ="Categories" #For Plural change in admin section
        
    def category_image(self):
        return mark_safe('<img scr="%s" width="50" height="50" />' %(self.image.url))
    
    def __str__(self):
        return self.title
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="pd", alphabet="abcde12345") #ven simply means vendor
    
    title = models.CharField(max_length=100, default="Nike") #Product Title
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default="This is a product")
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True) #Using the SET_NULL to maintain the product after user deletion
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True) #To filter based on Category
    
    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99") #2.99
    old_price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="2.99")
    
    specification = models.TextField(null=True, blank=True)
    tags = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
    
    product_status = models.CharField(choices=STATUS, max_length=10, default="in review")

    status = models.BooleanField(default=True) 
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False) #For digital product
    
    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")
    
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural ="Products" #For Plural change in admin section
        
    def category_image(self):
        return mark_safe('<img scr="%s" width="50" height="50" />' %(self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
    
#We are making an assumption that users may to upload more images
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural ="Product Images" #For Plural change in admin section





######## Cart, Order, OrderItems and Address ###########
class CartOrder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")
    paid_status = models.BooleanField(default=True)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    
    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
        order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
        product_status = models.CharField(max_length=200)
        item = models.CharField(max_length=200)
        image = models.CharField(max_length=200)
        qty = models.CharField(max_length=200)
        price = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")
        total = models.DecimalField(max_digits=999999999999, decimal_places=2, default="1.99")

        class Meta:
            verbose_name_plural = "Cart Order Items"

        def order_img(self):
            return mark_safe('<img scr="/media/%s" width="50" height="50" />' %(self.image))