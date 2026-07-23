from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Cuenta(TenantMixin):
    nombre_comercial = models.CharField(max_length=150)
    logotipo = models.ImageField(upload_to="logotipos/", null=True, blank=True)
    color_primario = models.CharField(max_length=7, default="#000000")
    color_secundario = models.CharField(max_length=7, default="#FFFFFF")
    zona_horaria = models.CharField(max_length=60, default="America/Argentina/Buenos_Aires")
    idioma = models.CharField(max_length=10, default="es-ar")
    estado = models.CharField(
        max_length=20,
        choices=(
            ("prueba", "Prueba"),
            ("activa", "Activa"),
            ("suspendida", "Suspendida"),
            ("cancelada", "Cancelada"),
        ),
        default="prueba",
    )
    creado_el = models.DateTimeField(auto_now_add=True)

    auto_create_schema = True

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"

    def __str__(self):
        return self.nombre_comercial


class Dominio(DomainMixin):
    class Meta:
        verbose_name = "Dominio"
        verbose_name_plural = "Dominios"
