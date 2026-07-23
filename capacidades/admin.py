from django.contrib import admin
from capacidades.models import Capacidad


@admin.register(Capacidad)
class CapacidadAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "plataforma",
        "nombre",
        "tipo",
        "disponibilidad",
        "estado_revision",
        "riesgo",
    )
    list_filter = (
        "plataforma",
        "disponibilidad",
        "estado_revision",
        "tipo",
        "categoria",
        "riesgo",
    )
    search_fields = (
        "codigo",
        "nombre",
        "permiso_requerido",
    )
