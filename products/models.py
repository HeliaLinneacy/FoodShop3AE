import random
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả danh mục")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.name

class Snack(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='snacks', verbose_name="Danh mục")
    snackName = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả sản phẩm")
    image = models.URLField(max_length=500, blank=True, null=True, verbose_name="Hình ảnh (URL)")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng")
    soldCount = models.IntegerField(default=0, verbose_name="Đã bán")
    status = models.BooleanField(default=True, verbose_name="Trạng thái (Còn bán)")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def save(self, *args, **kwargs):
        if not self.pk and self.soldCount == 0:
            self.soldCount = random.randint(20, 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.snackName
