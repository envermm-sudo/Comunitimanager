from django.db import models
from core.constantes import PLATAFORMAS, CATEGORIAS_INTENCION, NIVELES_RIESGO


class Capacidad(models.Model):
    plataforma = models.CharField(
        max_length=20,
        choices=PLATAFORMAS,
        verbose_name="Plataforma",
    )
    codigo = models.CharField(
        max_length=60,
        unique=True,
        verbose_name="Codigo",
    )
    nombre = models.CharField(
        max_length=120,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripcion",
    )
    permiso_requerido = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Permiso requerido",
    )
    disponibilidad = models.CharField(
        max_length=15,
        default="existe",
        choices=(
            ("existe", "Existe en la API"),
            ("no_existe", "No existe en la API"),
            ("prohibida", "Prohibida por la plataforma"),
        ),
        verbose_name="Disponibilidad",
    )
    estado_revision = models.CharField(
        max_length=15,
        default="no_solicitado",
        choices=(
            ("no_solicitado", "No solicitado"),
            ("en_revision", "En revision"),
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
        ),
        verbose_name="Estado de revision",
    )
    tipo = models.CharField(
        max_length=10,
        default="lectura",
        choices=(
            ("lectura", "Lectura"),
            ("escritura", "Escritura"),
        ),
        verbose_name="Tipo",
    )
    riesgo = models.CharField(
        max_length=10,
        default="bajo",
        choices=NIVELES_RIESGO,
        verbose_name="Nivel de riesgo",
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS_INTENCION,
        verbose_name="Categoria de intencion",
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
    )
    actualizado_el = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado el",
    )

    class Meta:
        verbose_name = "Capacidad"
        verbose_name_plural = "Capacidades"
        ordering = ("plataforma", "codigo")
        indexes = [
            models.Index(fields=("plataforma", "categoria")),
        ]

    def esta_disponible(self):
        return self.disponibilidad == "existe" and self.estado_revision == "aprobado"

    def habilitada_para(self, permisos_otorgados):
        if not self.esta_disponible():
            return False
        if not self.permiso_requerido:
            return True
        return self.permiso_requerido in permisos_otorgados

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
