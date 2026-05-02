from django.contrib import admin
from .models import Cart, CartDetail

class CartDetailInline(admin.TabularInline):
    model = CartDetail
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'totalAmount']
    inlines = [CartDetailInline]

admin.site.register(Cart, CartAdmin)
admin.site.register(CartDetail)
