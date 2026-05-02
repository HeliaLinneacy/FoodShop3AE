from django.db import models
from django.conf import settings
from products.models import Snack

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('approved', 'Đã duyệt'),
        ('shipped', 'Đang giao'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Người dùng")
    receiverName = models.CharField(max_length=255, verbose_name="Tên người nhận")
    phoneNumber = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    paymentMethod = models.CharField(max_length=50, default='COD', verbose_name="Phương thức thanh toán")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    createdDate = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")
    deliveryDate = models.DateTimeField(blank=True, null=True, verbose_name="Ngày giao hàng")
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tổng tiền")

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return f"Đơn hàng #{self.id} bởi {self.user.username}"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    snack = models.ForeignKey(Snack, on_delete=models.SET_NULL, null=True, verbose_name="Sản phẩm")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Đơn giá")
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Thành tiền")

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def __str__(self):
        return f"{self.quantity} x {self.snack.snackName if self.snack else 'Unknown'}"
