from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegisterForm(forms.ModelForm):  # No longer inheriting from UserCreationForm
    pin = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'PIN'}))

    class Meta:
        model = CustomUser
        fields = ['id', 'pin', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['id'].widget.attrs.update({'placeholder': 'ID'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['pin'])  # Set the PIN as the password
        if commit:
            user.save()
        return user
class UserChangeForm(forms.ModelForm):  # Preserved name
    class Meta:
        model = CustomUser
        fields = ['id', 'pin', 'email', 'phone_number', 'full_name', 'is_active', 'is_staff', 'is_superuser']  # Original fields
    
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['pin'].widget = forms.PasswordInput(attrs={'placeholder': 'PIN'})

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Full Name"}))
    bio = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Bio"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Phone"}))

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone']