from django.contrib import admin, messages
from .models import Order, OrderDetail

def cancel_selected_orders(modeladmin, request, queryset):
    count = 0
    for order in queryset.filter(status='pending'):
        order.status = 'cancelled'
        for item in order.items.all():
            if item.snack:
                item.snack.quantity += item.quantity
                item.snack.soldCount -= item.quantity
                item.snack.save()
        order.save()
        count += 1
    messages.success(request, f"Đã hủy và hoàn lại số lượng cho {count} đơn hàng.")
cancel_selected_orders.short_description = "Hủy đơn hàng (hoàn lại số lượng)"

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'receiverName', 'totalAmount', 'status', 'createdDate']
    list_filter = ['status', 'createdDate']
    search_fields = ['receiverName', 'phoneNumber']
    inlines = [OrderDetailInline]
    actions = [cancel_selected_orders]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail)
