from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import CustomUser


class UserRegisterForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ['id', 'pin']