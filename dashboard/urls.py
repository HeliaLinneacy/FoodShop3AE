from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
]
