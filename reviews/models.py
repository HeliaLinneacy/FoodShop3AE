from django.db import models
from django.conf import settings
from products.models import Snack

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Người dùng")
    snack = models.ForeignKey(Snack, on_delete=models.CASCADE, related_name='reviews', verbose_name="Sản phẩm")
    rating = models.IntegerField(default=5, verbose_name="Đánh giá (sao)")
    content = models.TextField(verbose_name="Nội dung")
    status = models.BooleanField(default=True, verbose_name="Trạng thái")
    createdDate = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"

    def __str__(self):
        return f"Đánh giá của {self.user.username} cho {self.snack.snackName}"
