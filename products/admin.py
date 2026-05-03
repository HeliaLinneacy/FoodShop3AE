from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Category, Snack


# ─── Category ───────────────────────────────────────────────────────────────

class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'description']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    ordering      = ['name']

    class Meta:
        verbose_name        = 'Danh mục'
        verbose_name_plural = 'Danh mục'


# ─── Snack ───────────────────────────────────────────────────────────────────

class SnackAdminForm(forms.ModelForm):
    price = forms.CharField(
        label="Giá (₫)",
        widget=forms.TextInput(attrs={'class': 'vTextField', 'placeholder': 'VD: 35.000'}),
    )

    class Meta:
        model  = Snack
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['price'] = f"{int(self.instance.price):,}".replace(",", ".")

    def clean_price(self):
        price_str = str(self.cleaned_data.get('price', ''))
        price_str = price_str.replace('.', '').replace(',', '')
        try:
            return float(price_str)
        except ValueError:
            raise forms.ValidationError("Giá không hợp lệ. Vui lòng nhập số (có thể dùng dấu chấm).")


class SnackAdmin(admin.ModelAdmin):
    form               = SnackAdminForm
    list_display       = ['id', 'snack_image_thumb', 'snackName', 'category', 'formatted_price', 'quantity', 'soldCount', 'status_badge']
    list_display_links = ['id', 'snackName']
    list_filter        = ['category', 'status']
    search_fields      = ['snackName', 'description']
    list_per_page      = 20
    ordering           = ['-id']
    readonly_fields    = ['snack_image_thumb']  # soldCount có thể nhập tay

    fieldsets = (
        ('📋 Thông tin cơ bản', {
            'fields': ('snackName', 'category', 'description', 'status'),
        }),
        ('💰 Giá & Kho hàng', {
            'fields': ('price', 'quantity', 'soldCount'),
            'description': '<small style="color:#888;">Lưu ý: Đã bán sẽ được cập nhật tự động khi có đơn hàng.</small>',
        }),
        ('🖼️ Hình ảnh', {
            'fields': ('image', 'snack_image_thumb'),
            'description': '<small style="color:#888;">Dán URL hình ảnh vào ô bên trên. Ảnh xem trước sẽ hiển thị bên dưới.</small>',
        }),
    )

    @admin.display(description='Ảnh')
    def snack_image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:6px;border:1px solid #ddd;">',
                obj.image
            )
        return format_html('<span style="color:#aaa;font-size:11px;">Chưa có ảnh</span>')

    @admin.display(description='Giá', ordering='price')
    def formatted_price(self, obj):
        price = int(obj.price)
        formatted = f"{price:,}".replace(",", ".")
        return format_html('<span style="color:#e53935;font-weight:600;">{} ₫</span>', formatted)

    @admin.display(description='Trạng thái', ordering='status', boolean=False)
    def status_badge(self, obj):
        if obj.status:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">✔ Đang bán</span>'
            )
        return format_html(
            '<span style="background:#dc3545;color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">✘ Ẩn</span>'
        )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Snack, SnackAdmin)
