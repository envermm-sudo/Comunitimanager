from datetime import timedelta
from django.db import models
from django.utils import timezone
from core.constantes import DIAS_GRACIA
from tenants.models import Cuenta


class Plan(models.Model):
    codigo = models.SlugField(max_length=30, unique=True, verbose_name="Codigo")
    nombre = models.CharField(max_length=60, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    precio_mensual = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Precio mensual"
    )
    moneda = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    max_negocios = models.PositiveSmallIntegerField(
        default=1, verbose_name="Maximo de negocios"
    )
    max_redes_por_negocio = models.PositiveSmallIntegerField(
        default=2, verbose_name="Maximo de redes por negocio"
    )
    max_publicaciones_mes = models.PositiveIntegerField(
        default=30, verbose_name="Maximo de publicaciones por mes"
    )
    max_tokens_mes = models.PositiveIntegerField(
        default=100000, verbose_name="Maximo de tokens de IA por mes"
    )
    max_usuarios = models.PositiveSmallIntegerField(
        default=1, verbose_name="Maximo de usuarios"
    )
    funcionalidades = models.JSONField(
        default=list, blank=True, verbose_name="Funcionalidades incluidas"
    )
    orden = models.PositiveSmallIntegerField(
        default=0, verbose_name="Orden de presentacion"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ("orden", "codigo")

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    cuenta = models.OneToOneField(
        Cuenta,
        on_delete=models.CASCADE,
        related_name="suscripcion",
        verbose_name="Cuenta",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="suscripciones",
        verbose_name="Plan",
    )
    estado = models.CharField(
        max_length=12,
        default="prueba",
        verbose_name="Estado",
        choices=(
            ("prueba", "En prueba"),
            ("activa", "Activa"),
            ("gracia", "En gracia"),
            ("morosa", "Morosa"),
            ("suspendida", "Suspendida"),
            ("cancelada", "Cancelada"),
        ),
    )
    inicio = models.DateField(verbose_name="Inicio")
    fin_prueba = models.DateField(null=True, blank=True, verbose_name="Fin de la prueba")
    proximo_cobro = models.DateField(null=True, blank=True, verbose_name="Proximo cobro")
    id_preaprobacion = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Identificador de preaprobacion",
    )
    cancelada_el = models.DateTimeField(
        null=True, blank=True, verbose_name="Cancelada el"
    )
    creada_el = models.DateTimeField(auto_now_add=True, verbose_name="Creada el")
    actualizada_el = models.DateTimeField(auto_now=True, verbose_name="Actualizada el")

    class Meta:
        verbose_name = "Suscripcion"
        verbose_name_plural = "Suscripciones"
        ordering = ("-creada_el",)

    def puede_publicar(self):
        return self.estado in ("prueba", "activa", "gracia")

    def puede_generar_contenido(self):
        return self.estado in ("prueba", "activa", "gracia")

    def es_solo_lectura(self):
        return self.estado in ("suspendida", "cancelada")

    def dias_de_atraso(self):
        if self.proximo_cobro is None:
            return 0
        diff = (timezone.localdate() - self.proximo_cobro).days
        return diff if diff > 0 else 0

    def estado_sugerido(self):
        if self.estado == "cancelada":
            return "cancelada"
        hoy = timezone.localdate()
        if self.fin_prueba is not None and hoy <= self.fin_prueba:
            return "prueba"
        atraso = self.dias_de_atraso()
        if atraso == 0:
            return "activa"
        if atraso <= DIAS_GRACIA:
            return "gracia"
        if atraso <= DIAS_GRACIA + 15:
            return "morosa"
        return "suspendida"

    def __str__(self):
        return f"{self.cuenta.nombre_comercial} - {self.plan.nombre}"


class Pago(models.Model):
    suscripcion = models.ForeignKey(
        Suscripcion,
        on_delete=models.CASCADE,
        related_name="pagos",
        verbose_name="Suscripcion",
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Monto"
    )
    moneda = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    estado = models.CharField(
        max_length=12,
        default="pendiente",
        verbose_name="Estado",
        choices=(
            ("pendiente", "Pendiente"),
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
            ("devuelto", "Devuelto"),
        ),
    )
    proveedor = models.CharField(
        max_length=20, default="mercadopago", verbose_name="Proveedor"
    )
    id_externo = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Identificador externo",
    )
    medio_pago = models.CharField(
        max_length=40, blank=True, verbose_name="Medio de pago"
    )
    periodo_desde = models.DateField(
        null=True, blank=True, verbose_name="Periodo desde"
    )
    periodo_hasta = models.DateField(
        null=True, blank=True, verbose_name="Periodo hasta"
    )
    pagado_el = models.DateTimeField(null=True, blank=True, verbose_name="Pagado el")
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ("-creado_el",)
        constraints = [
            models.UniqueConstraint(
                fields=("proveedor", "id_externo"),
                condition=~models.Q(id_externo=""),
                name="pago_externo_unico",
            )
        ]

    def __str__(self):
        return f"{self.monto} {self.moneda} {self.estado}"


class EventoPagoExterno(models.Model):
    proveedor = models.CharField(
        max_length=20, default="mercadopago", verbose_name="Proveedor"
    )
    tipo = models.CharField(max_length=40, verbose_name="Tipo de evento")
    clave_idempotencia = models.CharField(
        max_length=160, unique=True, verbose_name="Clave de idempotencia"
    )
    carga_util = models.JSONField(
        default=dict, verbose_name="Carga util recibida"
    )
    procesado = models.BooleanField(default=False, verbose_name="Procesado")
    intentos = models.PositiveSmallIntegerField(default=0, verbose_name="Intentos")
    mensaje_error = models.TextField(blank=True, verbose_name="Mensaje de error")
    procesado_el = models.DateTimeField(
        null=True, blank=True, verbose_name="Procesado el"
    )
    recibido_el = models.DateTimeField(
        auto_now_add=True, verbose_name="Recibido el"
    )

    class Meta:
        verbose_name = "Evento de pago externo"
        verbose_name_plural = "Eventos de pago externos"
        ordering = ("-recibido_el",)
        indexes = [models.Index(fields=("procesado", "recibido_el"))]

    def __str__(self):
        return f"{self.tipo} - {self.clave_idempotencia}"


class ConsumoIA(models.Model):
    cuenta = models.ForeignKey(
        Cuenta,
        on_delete=models.CASCADE,
        related_name="consumos",
        verbose_name="Cuenta",
    )
    periodo = models.DateField(
        verbose_name="Periodo",
        help_text="Primer dia del mes al que corresponde el consumo",
    )
    tokens_entrada = models.PositiveBigIntegerField(
        default=0, verbose_name="Tokens de entrada"
    )
    tokens_salida = models.PositiveBigIntegerField(
        default=0, verbose_name="Tokens de salida"
    )
    llamadas = models.PositiveIntegerField(
        default=0, verbose_name="Llamadas al modelo"
    )
    segundos_computo = models.PositiveIntegerField(
        default=0, verbose_name="Segundos de computo"
    )
    actualizado_el = models.DateTimeField(
        auto_now=True, verbose_name="Actualizado el"
    )

    class Meta:
        verbose_name = "Consumo de IA"
        verbose_name_plural = "Consumos de IA"
        ordering = ("-periodo",)
        constraints = [
            models.UniqueConstraint(
                fields=("cuenta", "periodo"),
                name="consumo_unico_por_cuenta_y_periodo",
            )
        ]

    def total_tokens(self):
        return self.tokens_entrada + self.tokens_salida

    def __str__(self):
        return f"{self.cuenta.nombre_comercial} - {self.periodo}"
