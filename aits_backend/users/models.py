from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 可以根据需求在这里增加其他字段，例如电话号码、职务等
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="电话")
    avatar = models.URLField(blank=True, null=True, verbose_name="头像")

    class Meta:
        db_table = "aits_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
