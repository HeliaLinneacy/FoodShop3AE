from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Trang quản trị cho Django"
admin.site.site_title = "Trang quản trị cho Django"
admin.site.index_title = "Trang chủ"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('chatbot/', include('chatbot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
