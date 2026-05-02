from django.db import models
from django.conf import settings
from products.models import Snack

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', verbose_name="Người dùng")
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tổng tiền")

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"

    def __str__(self):
        return f"Giỏ hàng của {self.user.username}"

class CartDetail(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Giỏ hàng")
    snack = models.ForeignKey(Snack, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Đơn giá")
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Thành tiền")

    class Meta:
        verbose_name = "Chi tiết giỏ hàng"
        verbose_name_plural = "Chi tiết giỏ hàng"

    def save(self, *args, **kwargs):
        self.totalPrice = self.quantity * self.unitPrice
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.snack.snackName}"
