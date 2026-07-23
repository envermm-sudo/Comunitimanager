from django.conf import settings
from django.db import models
from negocios.models import Negocio


class EventoBitacora(models.Model):
    # ADVERTENCIA: En el campo detalle nunca se deben guardar tokens, contrasenas ni claves.
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos",
        verbose_name="Negocio",
    )
    tipo_actor = models.CharField(
        max_length=10,
        default="usuario",
        choices=(
            ("usuario", "Usuario"),
            ("ia", "IA"),
            ("sistema", "Sistema"),
        ),
        verbose_name="Tipo de actor",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_bitacora",
        verbose_name="Actor",
    )
    accion = models.CharField(
        max_length=80,
        verbose_name="Accion",
    )
    objeto_tipo = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Tipo de objeto",
    )
    objeto_id = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Identificador del objeto",
    )
    detalle = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle",
    )
    resultado = models.CharField(
        max_length=10,
        default="exito",
        choices=(
            ("exito", "Exito"),
            ("error", "Error"),
        ),
        verbose_name="Resultado",
    )
    mensaje_error = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )
    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Direccion IP",
    )
    creado_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Evento de bitacora"
        verbose_name_plural = "Eventos de bitacora"
        ordering = ("-creado_el",)
        indexes = [
            models.Index(fields=("negocio", "creado_el")),
            models.Index(fields=("accion",)),
        ]

    def __str__(self):
        return f"{self.accion} - {self.creado_el}"
