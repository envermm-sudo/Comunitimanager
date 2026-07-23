from django.conf import settings
from django.db import models
from core.constantes import PLATAFORMAS, FORMATOS
from negocios.models import Negocio


class Estrategia(models.Model):
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name="estrategias",
        verbose_name="Negocio",
    )
    version = models.PositiveIntegerField(default=1, verbose_name="Version")
    estado = models.CharField(
        max_length=15,
        default="propuesta",
        verbose_name="Estado",
        choices=(
            ("propuesta", "Propuesta"),
            ("aprobada", "Aprobada"),
            ("vencida", "Vencida"),
        ),
    )
    periodo_desde = models.DateField(verbose_name="Periodo desde")
    periodo_hasta = models.DateField(verbose_name="Periodo hasta")
    objetivo = models.TextField(verbose_name="Objetivo")
    metrica_objetivo = models.CharField(
        max_length=60, blank=True, verbose_name="Metrica objetivo"
    )
    valor_meta = models.CharField(
        max_length=60, blank=True, verbose_name="Valor meta"
    )
    aprobada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estrategias_aprobadas",
        verbose_name="Aprobada por",
    )
    aprobada_el = models.DateTimeField(null=True, blank=True, verbose_name="Aprobada el")
    anterior = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="siguientes",
        verbose_name="Version anterior",
    )
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Estrategia"
        verbose_name_plural = "Estrategias"
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("negocio", "version"),
                name="estrategia_version_unica_por_negocio",
            )
        ]

    def __str__(self):
        return f"{self.negocio.nombre} v{self.version}"


class PilarContenido(models.Model):
    estrategia = models.ForeignKey(
        Estrategia,
        on_delete=models.CASCADE,
        related_name="pilares",
        verbose_name="Estrategia",
    )
    nombre = models.CharField(max_length=80, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    peso = models.PositiveSmallIntegerField(default=25, verbose_name="Peso")

    class Meta:
        verbose_name = "Pilar de contenido"
        verbose_name_plural = "Pilares de contenido"
        ordering = ("-peso",)

    def __str__(self):
        return self.nombre


class RitmoPublicacion(models.Model):
    estrategia = models.ForeignKey(
        Estrategia,
        on_delete=models.CASCADE,
        related_name="ritmos",
        verbose_name="Estrategia",
    )
    plataforma = models.CharField(
        max_length=20, choices=PLATAFORMAS, verbose_name="Plataforma"
    )
    formato = models.CharField(
        max_length=20, choices=FORMATOS, verbose_name="Formato"
    )
    veces_por_semana = models.PositiveSmallIntegerField(
        default=1, verbose_name="Veces por semana"
    )
    dias_preferidos = models.CharField(
        max_length=60, blank=True, verbose_name="Dias preferidos"
    )
    franja_horaria = models.CharField(
        max_length=40, blank=True, verbose_name="Franja horaria"
    )

    class Meta:
        verbose_name = "Ritmo de publicacion"
        verbose_name_plural = "Ritmos de publicacion"
        ordering = ("plataforma", "formato")

    def __str__(self):
        return f"{self.plataforma} - {self.formato}"
