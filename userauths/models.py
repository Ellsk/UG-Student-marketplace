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
        user.set_password(pin)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, pin, email=None, phone_number=None, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(id, pin, email, phone_number, full_name, **extra_fields)

class CustomUser(AbstractUser):
    id = models.CharField(max_length=10, unique=True, primary_key=True)
    pin = models.CharField(max_length=5)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['pin', 'email']

    objects = UserManager()

    def __str__(self):
        return self.id
