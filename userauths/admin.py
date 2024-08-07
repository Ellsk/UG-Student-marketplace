# Register your models here.
from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('id', 'pin', 'email', 'phone_number', 'full_name')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['pin'].widget = forms.PasswordInput(attrs={'placeholder': 'PIN'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["pin"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('id', 'pin', 'email', 'phone_number', 'full_name', 'is_active', 'is_staff', 'is_superuser')
    
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['pin'].widget = forms.PasswordInput(attrs={'placeholder': 'PIN'})

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'email', 'phone_number', 'full_name', 'is_staff', 'is_superuser')
    search_fields = ('id', 'email', 'phone_number', 'full_name')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('id', 'pin', 'email', 'phone_number', 'full_name', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id', 'pin', 'email', 'phone_number', 'full_name', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(CustomUser, UserAdmin)
