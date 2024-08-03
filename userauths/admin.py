from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm
from django import forms

class UserCreationForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('id', 'pin', 'email', 'phone_number', 'full_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["pin"])
        if commit:
            user.save()
        return user

class UserChangeForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('id', 'pin', 'email', 'phone_number', 'full_name', 'is_active', 'is_staff', 'is_superuser')

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'email', 'phone_number', 'full_name', 'is_staff', 'is_superuser')
    search_fields = ('id', 'email', 'phone_number', 'full_name')
    ordering = ('id',)

admin.site.register(CustomUser, UserAdmin)
