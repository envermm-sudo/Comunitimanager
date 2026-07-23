from django.db import models
from django.utils import timezone
from negocios.models import Negocio


class Briefing(models.Model):
    negocio = models.OneToOneField(
        Negocio,
        on_delete=models.CASCADE,
        related_name="briefing",
        verbose_name="Negocio",
    )
    completitud = models.PositiveSmallIntegerField(
        default=0, verbose_name="Completitud"
    )
    actualizado_el = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Briefing"
        verbose_name_plural = "Briefings"

    def __str__(self):
        return f"Briefing de {self.negocio.nombre}"


class HechoBriefing(models.Model):
    briefing = models.ForeignKey(
        Briefing,
        on_delete=models.CASCADE,
        related_name="hechos",
        verbose_name="Briefing",
    )
    categoria = models.CharField(
        max_length=20,
        verbose_name="Categoria",
        choices=(
            ("oferta", "Oferta"),
            ("operacion", "Operacion"),
            ("diferencial", "Diferencial"),
            ("restriccion", "Restriccion"),
            ("activos", "Activos"),
        ),
    )
    clave = models.CharField(max_length=100, verbose_name="Clave")
    valor = models.TextField(verbose_name="Valor")
    origen = models.CharField(
        max_length=10,
        default="dicho",
        verbose_name="Origen",
        choices=(
            ("dicho", "Dicho por el usuario"),
            ("deducido", "Deducido por la IA"),
        ),
    )
    confianza = models.CharField(
        max_length=10,
        default="alta",
        verbose_name="Confianza",
        choices=(
            ("alta", "Alta"),
            ("media", "Media"),
            ("baja", "Baja"),
        ),
    )
    confirmado = models.BooleanField(default=False, verbose_name="Confirmado por el usuario")
    vigente_desde = models.DateField(null=True, blank=True, verbose_name="Vigente desde")
    vigente_hasta = models.DateField(null=True, blank=True, verbose_name="Vigente hasta")
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Hecho del briefing"
        verbose_name_plural = "Hechos del briefing"
        ordering = ("categoria", "clave")
        indexes = [
            models.Index(fields=("briefing", "categoria")),
        ]

    def esta_vigente(self):
        hoy = timezone.localdate()
        if self.vigente_desde is not None and hoy < self.vigente_desde:
            return False
        if self.vigente_hasta is not None and hoy > self.vigente_hasta:
            return False
        return True

    def __str__(self):
        return f"{self.clave}: {self.valor}"
