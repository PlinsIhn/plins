from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, role=None, **extra_fields):
        if not phone:
            raise ValueError("Tsy maintsy numero telephone anao")
        if not role:
            raise ValueError("Mpivarotra sa Mpividy")

        user = self.model(phone=phone, role=role, **extra_fields)

        if not password:
            raise ValueError("Mila mot de passe")
        user.set_password(password)

        if role == 'acheteur':
            user.is_active = True

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('role', 'vendeur')  # facultatif mais utile
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('vendeur', 'vendeur'),
        ('acheteur', 'acheteur'),
    )

    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.phone} ({self.role})"
