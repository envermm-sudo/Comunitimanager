from django.contrib import admin
from .models import Conversacion, Mensaje, AccionPendiente, ReglaPermanente


class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 0
    readonly_fields = (
        "rol",
        "contenido",
        "modelo_usado",
        "tokens_entrada",
        "tokens_salida",
        "latencia_ms",
        "creado_el",
    )


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    inlines = (MensajeInline,)
    list_display = (
        "__str__",
        "usuario",
        "negocio_activo",
        "estado",
        "actualizada_el",
    )
    list_filter = ("estado",)


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("conversacion", "rol", "creado_el")
    list_filter = ("rol",)
    search_fields = ("contenido",)


@admin.register(AccionPendiente)
class AccionPendienteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_capacidad",
        "negocio",
        "riesgo",
        "codigo_confirmacion",
        "estado",
        "vence_el",
    )
    list_filter = ("estado", "riesgo", "codigo_capacidad")
    search_fields = ("codigo_capacidad", "descripcion")
    readonly_fields = (
        "codigo_confirmacion",
        "creada_el",
        "confirmada_el",
        "ejecutada_el",
    )


@admin.register(ReglaPermanente)
class ReglaPermanenteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_capacidad",
        "negocio",
        "activa",
        "veces_aplicada",
        "ultima_aplicacion",
    )
    list_filter = ("activa", "codigo_capacidad")
    search_fields = ("codigo_capacidad", "condicion")
