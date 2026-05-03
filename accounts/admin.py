from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


class CustomUserAdmin(UserAdmin):
    model              = User
    list_display       = ['username', 'fullName', 'email', 'phone_display', 'role_badge', 'status_badge', 'is_staff']
    list_display_links = ['username', 'fullName']
    list_filter        = ['role', 'status', 'is_staff', 'is_active']
    search_fields      = ['username', 'email', 'fullName', 'phoneNumber']
    ordering           = ['-date_joined']
    list_per_page      = 25

    fieldsets = UserAdmin.fieldsets + (
        ('📋 Thông tin bổ sung', {
            'fields': ('fullName', 'phoneNumber', 'address', 'role', 'status'),
        }),
    )

    @admin.display(description='Số điện thoại')
    def phone_display(self, obj):
        if obj.phoneNumber:
            return format_html('<span style="color:#555;">{}</span>', obj.phoneNumber)
        return format_html('<span style="color:#bbb;font-size:11px;">Chưa có</span>')

    @admin.display(description='Vai trò', ordering='role')
    def role_badge(self, obj):
        if obj.role == 'admin':
            return format_html(
                '<span style="background:#6f42c1;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">👑 Admin</span>'
            )
        return format_html(
            '<span style="background:#17a2b8;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">🛒 Khách</span>'
        )

    @admin.display(description='Trạng thái', ordering='status')
    def status_badge(self, obj):
        if obj.status:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">✔ Hoạt động</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">✘ Khóa</span>'
        )


admin.site.register(User, CustomUserAdmin)
