from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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

    def __str__(self):
        return self.id


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images")  # Adjusted upload_to to "images"
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)  # Adjusted to match phone_number format
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.id} - {self.full_name} - {self.bio}"