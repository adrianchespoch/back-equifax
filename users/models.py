from django.db import models

from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager
)

from backend.shared.models.models import AuditDateModel




# ### Custom User Model: debemos registrarlo en Django para q lo use en lugar del x default
class CustomUserManager(UserManager):
    def _create_user(self, email, password, username, **extra_fields):
        # if not email:
        #     raise ValueError('Invalid email')

        email = self.normalize_email(email) if email else None
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_user(self, email=None, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', False) # is_staff false = NO Admin
        return self._create_user(email, password, username, **extra_fields)


    def create_superuser(self, email=None, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) # is_staff true = Admin
        return self._create_user(email, password, username, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AuditDateModel):
    email = models.CharField(max_length=100, unique=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    avatar = models.ImageField(default='avatar.png')
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False) # admin?
    objects = CustomUserManager() # 
    # USERNAME_FIELD = 'email' # django username = email
    USERNAME_FIELD = 'username' # django username = username
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']) # create index for email
        ]

