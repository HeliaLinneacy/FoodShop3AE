import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snack_shop.settings')
django.setup()

from products.models import Snack
from cart.models import Cart, CartDetail
from orders.models import Order, OrderDetail

RATE = 25000

for snack in Snack.objects.all():
    snack.price = snack.price * RATE
    snack.save()

for item in CartDetail.objects.all():
    item.unitPrice = item.unitPrice * RATE
    item.totalPrice = item.totalPrice * RATE
    item.save()

for cart in Cart.objects.all():
    cart.totalAmount = cart.totalAmount * RATE
    cart.save()

for item in OrderDetail.objects.all():
    item.unitPrice = item.unitPrice * RATE
    item.totalPrice = item.totalPrice * RATE
    item.save()

for order in Order.objects.all():
    order.totalAmount = order.totalAmount * RATE
    order.save()

print("Prices updated successfully!")
