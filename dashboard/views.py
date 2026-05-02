from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from orders.models import Order
from products.models import Snack
from accounts.models import User
from django.db.models import Sum

@staff_member_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('totalAmount'))['totalAmount__sum'] or 0
    total_products = Snack.objects.count()
    total_users = User.objects.filter(role='customer').count()
    
    recent_orders = Order.objects.all().order_by('-createdDate')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)

@staff_member_required
def order_management(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all().order_by('-createdDate')
    if status_filter:
        orders = orders.filter(status=status_filter)

    STATUS_LABELS = {
        'pending': ('Chờ Xử Lý', 'warning'),
        'approved': ('Đã Duyệt', 'info'),
        'shipped': ('Đang Giao', 'primary'),
        'delivered': ('Đã Giao Hàng', 'success'),
        'cancelled': ('Đã Hủy', 'danger'),
    }

    context = {
        'orders': orders,
        'orders_count_all': Order.objects.count(),
        'status_filter': status_filter,
        'STATUS_LABELS': STATUS_LABELS,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_management.html', context)

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = order.status
            # If cancelled from non-cancelled: restore stock
            if new_status == 'cancelled' and old_status != 'cancelled':
                for item in order.items.all():
                    if item.snack:
                        item.snack.quantity += item.quantity
                        item.snack.soldCount -= item.quantity
                        item.snack.save()
            # If un-cancelling: deduct stock again
            elif old_status == 'cancelled' and new_status != 'cancelled':
                for item in order.items.all():
                    if item.snack:
                        item.snack.quantity -= item.quantity
                        item.snack.soldCount += item.quantity
                        item.snack.save()
            order.status = new_status
            order.save()
            messages.success(request, f'Đã cập nhật trạng thái đơn hàng #{ order.id }.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    return redirect('dashboard:order_management')
