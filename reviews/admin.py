from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'snack', 'rating', 'status', 'createdDate']
    list_filter = ['rating', 'status']
    search_fields = ['content']

admin.site.register(Review, ReviewAdmin)
