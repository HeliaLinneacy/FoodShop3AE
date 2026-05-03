from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Order, OrderDetail


# ─── Action ──────────────────────────────────────────────────────────────────

def cancel_selected_orders(modeladmin, request, queryset):
    count = 0
    for order in queryset.filter(status='pending'):
        order.status = 'cancelled'
        for item in order.items.all():
            if item.snack:
                item.snack.quantity  += item.quantity
                item.snack.soldCount -= item.quantity
                item.snack.save()
        order.save()
        count += 1
    messages.success(request, f"Đã hủy và hoàn lại số lượng cho {count} đơn hàng.")

cancel_selected_orders.short_description = "🚫 Hủy đơn hàng đã chọn (hoàn kho)"


# ─── OrderDetail inline ───────────────────────────────────────────────────────

class OrderDetailInline(admin.TabularInline):
    model       = OrderDetail
    extra       = 0
    readonly_fields = ['snack', 'quantity', 'unitPrice', 'totalPrice']
    can_delete  = False
    verbose_name        = 'Chi tiết sản phẩm'
    verbose_name_plural = 'Chi tiết sản phẩm'


# ─── Order ────────────────────────────────────────────────────────────────────

STATUS_COLORS = {
    'pending':    ('#f39c12', '⏳ Chờ xử lý'),
    'approved':   ('#3498db', '✔ Đã duyệt'),
    'shipped':    ('#8e44ad', '🚚 Đang giao'),
    'delivered':  ('#27ae60', '📦 Đã giao'),
    'cancelled':  ('#e74c3c', '✘ Đã hủy'),
}

class OrderAdmin(admin.ModelAdmin):
    list_display       = ['id', 'receiver_info', 'formatted_total', 'status_badge', 'createdDate']
    list_display_links = ['id', 'receiver_info']
    list_filter        = ['status', 'createdDate']
    search_fields      = ['receiverName', 'phoneNumber', 'user__username']
    inlines            = [OrderDetailInline]
    actions            = [cancel_selected_orders]
    list_per_page      = 25
    ordering           = ['-createdDate']
    readonly_fields    = ['createdDate', 'user']

    fieldsets = (
        ('👤 Thông tin người nhận', {
            'fields': ('user', 'receiverName', 'phoneNumber', 'address'),
        }),
        ('💰 Thanh toán & Trạng thái', {
            'fields': ('totalAmount', 'status'),
        }),
        ('🕐 Thời gian', {
            'fields': ('createdDate',),
        }),
    )

    @admin.display(description='Người nhận', ordering='receiverName')
    def receiver_info(self, obj):
        return format_html(
            '<b>{}</b><br><small style="color:#888;">{}</small>',
            obj.receiverName, obj.phoneNumber or ''
        )

    @admin.display(description='Tổng tiền', ordering='totalAmount')
    def formatted_total(self, obj):
        amount = int(obj.totalAmount)
        formatted = f"{amount:,}".replace(",", ".")
        return format_html('<b style="color:#e53935;">{} ₫</b>', formatted)

    @admin.display(description='Trạng thái', ordering='status')
    def status_badge(self, obj):
        color, label = STATUS_COLORS.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;white-space:nowrap;">{}</span>',
            color, label
        )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail)
