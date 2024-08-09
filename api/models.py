from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import CustomUser

def user_directory_path(instance, filename):
    return 'user_(0)/(1)'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcde12345") #cat simply means category
    title = models.CharField(max_length=100) #Product Title
    image = models.ImageField(upload_to="category")
    
    class Meta:
        verbose_name_plural ="Categories" #For Plural change in admin section
        
    def category_image(self):
        return mark_safe('<img scr="%s" width="50" height="50" />' %(self.image.url))
    
    def __str__(self):
        return self.title
    #Since the cid is calculated automatically we return only title and image scr
    
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcde12345") #ven simply means vendor
    
    title = models.CharField(max_length=100) #Vendor Product Title
    image = models.ImageField(upload_to=user_directory_path) # Instead of uploading to separate image product file lets relate each vendor with his own product upload path
    description = models.TextField(null=True, blank=True)
    
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