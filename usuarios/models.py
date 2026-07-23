from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Correo electronico")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, blank=True, verbose_name="Apellido")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es parte del staff")
    fecha_alta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de alta")

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}".strip()

    def get_short_name(self):
        return self.nombre
