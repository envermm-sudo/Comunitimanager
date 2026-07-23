from django.conf import settings
from django.db import models


class Negocio(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    rubro = models.CharField(max_length=100, verbose_name="Rubro")
    zona_horaria = models.CharField(
        max_length=60,
        default="America/Argentina/Buenos_Aires",
        verbose_name="Zona horaria",
    )
    estado = models.CharField(
        max_length=20,
        verbose_name="Estado",
        default="activo",
        choices=(
            ("activo", "Activo"),
            ("pausado", "Pausado"),
            ("archivado", "Archivado"),
        ),
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="negocios_creados",
        verbose_name="Creado por",
    )
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Negocio"
        verbose_name_plural = "Negocios"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre
