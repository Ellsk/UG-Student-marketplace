
from datetime import timezone
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from taggit.managers import TaggableManager


class UserManager(BaseUserManager):
    def create_user(self, id, pin, email=None, phone_number=None, full_name=None, **extra_fields):
        if not id:
            raise ValueError('The ID must be set')
        if not pin:
            raise ValueError('The PIN must be set')

        email = self.normalize_email(email)
        user = self.model(id=id, email=email, phone_number=phone_number, full_name=full_name, **extra_fields)
        user.set_password(pin)  # Encrypt the pin as password
        user.save(using=self._db)
        return user

    def create_superuser(self, id, pin, email=None, phone_number=None, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(id, pin, email, phone_number, full_name, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Explicitly remove the username field
    id = models.CharField(max_length=10, unique=True, primary_key=True)
    pin = models.CharField(max_length=5)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['pin', 'email', 'first_name', 'last_name']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.email:
            email_username, phone_number = self.email.split("@")[0], self.phone_number
            # Set full name if not provided
            if not self.full_name:
                self.full_name = email_username
            # Set username if not provided
            if not self.username:
                self.username = email_username
        
        # Call the parent's save method
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.id


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.FileField(upload_to="images", null=True, blank=True)  # Adjusted upload_to to "images"
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)  # Adjusted to match phone_number format
    verified = models.BooleanField(default=False)
    
    #Blog Info
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)  # No auto_now_add

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.id} - {self.full_name} - {self.bio}"
    

class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200) 
    subject = models.CharField(max_length=200)
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name

#For the
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user=instance,
            full_name=instance.full_name,
            phone=instance.phone_number,
            date=timezone.now()  # Set date to current time when profile is created
        )
    else:
        instance.profile.full_name = instance.full_name
        instance.profile.phone = instance.phone_number
        instance.profile.save()
        
        
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
post_save.connect(create_user_profile, sender=CustomUser)
post_save.connect(save_user_profile, sender=CustomUser)

class ResourceCategory(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="rcat", alphabet="abcde12345")
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    rid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="res", alphabet="abcde12345")
    title = models.CharField(max_length=200)
    content = models.TextField()  # This could include text, links to articles, videos, etc.
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name="resources")
    tags = TaggableManager(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class UserResourceInteraction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # Example: "viewed", "liked", "shared"
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.resource.title} - {self.action}"
