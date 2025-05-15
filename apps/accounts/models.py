from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)  # 사용자 이메일, 고유
    phone_number = models.CharField(max_length=15, blank=True)  # 전화번호
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    # related_name을 Django AbstractUser 기본값으로 사용하도록 수정
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     # related_name='user_set', # Django default
    #     # related_query_name='user',
    #     blank=True,
    #     verbose_name='groups',
    #     help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     # related_name='user_set', # Django default
    #     # related_query_name='user',
    #     blank=True,
    #     verbose_name='user permissions',
    #     help_text='Specific permissions for this user.',
    # )

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'accounts'