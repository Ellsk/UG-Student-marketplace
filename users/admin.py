# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'id_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('id_number', 'pin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('id_number', 'pin')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)