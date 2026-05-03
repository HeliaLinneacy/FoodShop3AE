from django.contrib import admin
from django.utils.html import format_html
from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display       = ['id', 'user', 'snack_link', 'star_display', 'short_content', 'status_badge', 'createdDate']
    list_display_links = ['id', 'user']
    list_filter        = ['rating', 'status', 'createdDate']
    search_fields      = ['content', 'user__username', 'snack__snackName']
    list_per_page      = 25
    ordering           = ['-createdDate']
    readonly_fields    = ['user', 'snack', 'rating', 'content', 'createdDate']
    actions            = ['approve_reviews', 'reject_reviews']

    fieldsets = (
        ('📋 Nội dung đánh giá', {
            'fields': ('user', 'snack', 'rating', 'content', 'createdDate'),
        }),
        ('⚙️ Kiểm duyệt', {
            'fields': ('status',),
        }),
    )

    @admin.display(description='Sản phẩm', ordering='snack__snackName')
    def snack_link(self, obj):
        if obj.snack:
            return format_html('<span style="color:#1a73e8;">{}</span>', obj.snack.snackName)
        return '—'

    @admin.display(description='Sao', ordering='rating')
    def star_display(self, obj):
        stars = '⭐' * int(obj.rating) if obj.rating else '—'
        return format_html('<span title="{} sao">{}</span>', obj.rating, stars)

    @admin.display(description='Nội dung')
    def short_content(self, obj):
        if obj.content:
            short = obj.content[:60] + ('…' if len(obj.content) > 60 else '')
            return format_html('<span style="color:#555;">{}</span>', short)
        return '—'

    @admin.display(description='Trạng thái', ordering='status')
    def status_badge(self, obj):
        if obj.status:
            return format_html(
                '<span style="background:#28a745;color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">✔ Đã duyệt</span>'
            )
        return format_html(
            '<span style="background:#fd7e14;color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">⏳ Chờ duyệt</span>'
        )

    @admin.action(description='✅ Phê duyệt đánh giá đã chọn')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f"Đã phê duyệt {updated} đánh giá.")

    @admin.action(description='🚫 Từ chối đánh giá đã chọn')
    def reject_reviews(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f"Đã từ chối {updated} đánh giá.")


admin.site.register(Review, ReviewAdmin)
