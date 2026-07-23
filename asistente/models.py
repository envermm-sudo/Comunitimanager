import secrets
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from core.constantes import ALFABETO_CODIGO, HORAS_VIGENCIA_ACCION, NIVELES_RIESGO
from negocios.models import Negocio
from redes.models import RedConectada


def vencimiento_por_defecto():
    return timezone.now() + timedelta(hours=HORAS_VIGENCIA_ACCION)


class Conversacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversaciones",
        verbose_name="Usuario"
    )
    negocio_activo = models.ForeignKey(
        Negocio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversaciones",
        verbose_name="Negocio activo"
    )
    titulo = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Titulo"
    )
    estado = models.CharField(
        max_length=12,
        default="activa",
        verbose_name="Estado",
        choices=(
            ("activa", "Activa"),
            ("archivada", "Archivada"),
        )
    )
    creada_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada el"
    )
    actualizada_el = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el"
    )

    class Meta:
        verbose_name = "Conversacion"
        verbose_name_plural = "Conversaciones"
        ordering = ("-actualizada_el",)

    def __str__(self):
        if self.titulo:
            return self.titulo
        return f"Conversacion {self.pk}"


class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name="mensajes",
        verbose_name="Conversacion"
    )
    rol = models.CharField(
        max_length=10,
        verbose_name="Rol",
        choices=(
            ("usuario", "Usuario"),
            ("asistente", "Asistente"),
            ("sistema", "Sistema"),
        )
    )
    contenido = models.TextField(
        verbose_name="Contenido"
    )
    modelo_usado = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Modelo usado"
    )
    tokens_entrada = models.PositiveIntegerField(
        default=0,
        verbose_name="Tokens de entrada"
    )
    tokens_salida = models.PositiveIntegerField(
        default=0,
        verbose_name="Tokens de salida"
    )
    latencia_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Latencia en milisegundos"
    )
    creado_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el"
    )

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ("creado_el",)
        indexes = [
            models.Index(fields=("conversacion", "creado_el")),
        ]

    def __str__(self):
        return f"{self.rol}: {self.contenido[:50]}"


class AccionPendiente(models.Model):
    # IMPORTANTE: en el campo carga_util nunca se deben guardar tokens ni claves.
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name="acciones",
        verbose_name="Negocio"
    )
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        verbose_name="Conversacion"
    )
    mensaje_origen = models.ForeignKey(
        Mensaje,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        verbose_name="Mensaje de origen"
    )
    red = models.ForeignKey(
        RedConectada,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        verbose_name="Red conectada"
    )
    codigo_capacidad = models.CharField(
        max_length=60,
        verbose_name="Codigo de capacidad"
    )
    descripcion = models.TextField(
        verbose_name="Que se va a hacer"
    )
    justificacion = models.TextField(
        blank=True,
        verbose_name="Por que se propone"
    )
    advertencia = models.TextField(
        blank=True,
        verbose_name="Advertencia"
    )
    carga_util = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Carga util"
    )
    riesgo = models.CharField(
        max_length=10,
        default="medio",
        choices=NIVELES_RIESGO,
        verbose_name="Nivel de riesgo"
    )
    verbo = models.CharField(
        max_length=40,
        default="CONFIRMAR",
        verbose_name="Verbo"
    )
    codigo_confirmacion = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="Codigo de confirmacion"
    )
    estado = models.CharField(
        max_length=12,
        default="pendiente",
        verbose_name="Estado",
        choices=(
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("rechazada", "Rechazada"),
            ("vencida", "Vencida"),
            ("ejecutada", "Ejecutada"),
            ("fallida", "Fallida"),
        )
    )
    vence_el = models.DateTimeField(
        default=vencimiento_por_defecto,
        verbose_name="Vence el"
    )
    confirmada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones_confirmadas",
        verbose_name="Confirmada por"
    )
    confirmada_el = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Confirmada el"
    )
    ejecutada_el = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ejecutada el"
    )
    resultado = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado"
    )
    mensaje_error = models.TextField(
        blank=True,
        verbose_name="Mensaje de error"
    )
    creada_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada el"
    )

    class Meta:
        verbose_name = "Accion pendiente"
        verbose_name_plural = "Acciones pendientes"
        ordering = ("-creada_el",)
        constraints = [
            models.UniqueConstraint(
                fields=("codigo_confirmacion",),
                condition=Q(estado="pendiente") & ~Q(codigo_confirmacion=""),
                name="codigo_confirmacion_unico_entre_pendientes"
            ),
        ]
        indexes = [
            models.Index(fields=("negocio", "estado")),
        ]

    @staticmethod
    def generar_sufijo():
        return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(3))

    def esta_vigente(self):
        return self.estado == "pendiente" and timezone.now() < self.vence_el

    def normalizar(self, texto):
        if texto is None:
            return ""
        return " ".join(texto.split()).upper()

    def coincide_codigo(self, texto):
        if not self.esta_vigente():
            return False
        if self.riesgo == "bajo" and not self.codigo_confirmacion:
            return True
        return self.normalizar(texto) == self.normalizar(self.codigo_confirmacion)

    def save(self, *args, **kwargs):
        if not self.codigo_confirmacion and self.riesgo != "bajo":
            self.codigo_confirmacion = f"{self.verbo} {self.generar_sufijo()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_capacidqad} - {self.estado}"


class ReglaPermanente(models.Model):
    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name="reglas",
        verbose_name="Negocio"
    )
    codigo_capacidad = models.CharField(
        max_length=60,
        verbose_name="Codigo de capacidad"
    )
    condicion = models.TextField(
        verbose_name="Cuando se aplica"
    )
    criterio = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Criterio"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )
    creada_desde = models.ForeignKey(
        Mensaje,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reglas",
        verbose_name="Mensaje de origen"
    )
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reglas_creadas",
        verbose_name="Creada por"
    )
    veces_aplicada = models.PositiveIntegerField(
        default=0,
        verbose_name="Veces aplicada"
    )
    ultima_aplicacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ultima aplicacion"
    )
    creada_el = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada el"
    )

    class Meta:
        verbose_name = "Regla permanente"
        verbose_name_plural = "Reglas permanentes"
        ordering = ("-creada_el",)

    def clean(self):
        from capacidades.models import Capacidad
        capacidad = Capacidad.objects.filter(codigo=self.codigo_capacidad).first()
        if not capacidad:
            raise ValidationError("La capacidad indicada no existe en el catalogo.")
        if capacidad.categoria == "contenido":
            raise ValidationError(
                "Las reglas permanentes no pueden automatizar la publicacion de contenido. "
                "Toda publicacion requiere aprobacion del usuario."
            )
        if capacidad.tipo != "escritura":
            raise ValidationError("Las reglas permanentes solo aplican a acciones de escritura.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_capacidad} en {self.negocio}"
