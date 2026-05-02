from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'fullName', 'role', 'status', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('fullName', 'phoneNumber', 'address', 'role', 'status')}),
    )

admin.site.register(User, CustomUserAdmin)
