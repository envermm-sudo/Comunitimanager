from django.db import models
from django.utils import timezone
from core.campos import CampoCifrado
from core.constantes import PLATAFORMAS
from negocios.models import Negocio


class RedConectada(models.Model):
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name="redes",
        verbose_name="Negocio",
    )
    plataforma = models.CharField(
        max_length=20,
        choices=PLATAFORMAS,
        verbose_name="Plataforma",
    )
    id_externo = models.CharField(
        max_length=120,
        verbose_name="Identificador en la red",
    )
    nombre_externo = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre de la cuenta en la red",
    )
    estado = models.CharField(
        max_length=20,
        default="activa",
        verbose_name="Estado",
        choices=(
            ("activa", "Activa"),
            ("token_vencido", "Token vencido"),
            ("revocada", "Revocada"),
            ("error", "Con error"),
        ),
    )
    conectada_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Conectada el",
    )
    actualizada_el = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el",
    )

    class Meta:
        verbose_name = "Red conectada"
        verbose_name_plural = "Redes conectadas"
        ordering = ("negocio", "plataforma")
        constraints = [
            models.UniqueConstraint(
                fields=("negocio", "plataforma", "id_externo"),
                name="red_unica_por_negocio",
            )
        ]
        indexes = [
            models.Index(fields=("negocio", "plataforma")),
        ]

    def __str__(self):
        return f"{self.negocio.nombre} - {self.plataforma}"


class CredencialOAuth(models.Model):
    red = models.OneToOneField(
        RedConectada,
        on_delete=models.CASCADE,
        related_name="credencial",
        verbose_name="Red conectada",
    )
    token_acceso = CampoCifrado(
        verbose_name="Token de acceso",
    )
    token_refresco = CampoCifrado(
        blank=True,
        null=True,
        verbose_name="Token de refresco",
    )
    permisos = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Permisos otorgados",
    )
    vence_el = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Vence el",
    )
    ultimo_refresco = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ultimo refresco",
    )
    estado = models.CharField(
        max_length=15,
        default="vigente",
        verbose_name="Estado",
        choices=(
            ("vigente", "Vigente"),
            ("por_vencer", "Por vencer"),
            ("vencida", "Vencida"),
            ("revocada", "Revocada"),
        ),
    )
    creada_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada el",
    )
    actualizada_el = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el",
    )

    class Meta:
        verbose_name = "Credencial OAuth"
        verbose_name_plural = "Credenciales OAuth"

    def dias_para_vencer(self):
        if self.vence_el is None:
            return None
        return (self.vence_el - timezone.now()).days

    def necesita_refresco(self):
        dias = self.dias_para_vencer()
        if dias is None:
            return False
        return dias <= 7

    def __str__(self):
        return f"Credencial de {self.red}"
