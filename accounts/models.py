from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Quản trị viên'),
        ('customer', 'Khách hàng'),
    )
    fullName = models.CharField(max_length=255, blank=True, null=True, verbose_name="Họ và tên")
    phoneNumber = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name="Vai trò")
    status = models.BooleanField(default=True, verbose_name="Trạng thái")

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return self.username
