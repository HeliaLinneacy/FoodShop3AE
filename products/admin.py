from django.contrib import admin
from django import forms
from .models import Category, Snack

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']

class SnackAdminForm(forms.ModelForm):
    price = forms.CharField(label="Price", widget=forms.TextInput(attrs={'class': 'vTextField'}))

    class Meta:
        model = Snack
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
            raise forms.ValidationError("Giá không hợp lệ. Vui lòng nhập số, có thể dùng dấu chấm phân cách.")

class SnackAdmin(admin.ModelAdmin):
    form = SnackAdminForm
    list_display = ['id', 'snackName', 'category', 'price', 'quantity', 'status']
    list_filter = ['category', 'status']
    search_fields = ['snackName', 'description']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Snack, SnackAdmin)
