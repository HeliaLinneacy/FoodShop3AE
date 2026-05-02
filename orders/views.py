from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderDetail
from cart.models import Cart
from django.contrib import messages

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')

    if request.method == 'POST':
        receiverName = request.POST.get('receiverName')
        phoneNumber = request.POST.get('phoneNumber')
        address = request.POST.get('address')
        note = request.POST.get('note')
        paymentMethod = request.POST.get('paymentMethod', 'COD')

        order = Order.objects.create(
            user=request.user,
            receiverName=receiverName,
            phoneNumber=phoneNumber,
            address=address,
            note=note,
            paymentMethod=paymentMethod,
            totalAmount=cart.totalAmount
        )

        for item in cart.items.all():
            OrderDetail.objects.create(
                order=order,
                snack=item.snack,
                quantity=item.quantity,
                unitPrice=item.unitPrice,
                totalPrice=item.totalPrice
            )
            item.snack.quantity -= item.quantity
            item.snack.soldCount += item.quantity
            item.snack.save()

        # Clear cart
        cart.items.all().delete()
        cart.totalAmount = 0
        cart.save()

        messages.success(request, "Order placed successfully!")
        return redirect('orders:order_history')

    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-createdDate')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        for item in order.items.all():
            item.snack.quantity += item.quantity
            item.snack.soldCount -= item.quantity
            item.snack.save()
        order.save()
        messages.success(request, f"Đã hủy đơn hàng #{order.id} thành công.")
    else:
        messages.error(request, "Không thể hủy đơn hàng này.")
    return redirect('orders:order_history')
