# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    id_number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'ID Number'}))
    pin = forms.CharField(max_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'PIN'}))
