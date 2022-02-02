from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_ROLES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(
        max_length=16,
        choices=USER_ROLES,
        default='user'
    )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
