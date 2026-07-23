from django.contrib import admin
from .models import Plan, Suscripcion, Pago, EventoPagoExterno, ConsumoIA


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "codigo",
        "precio_mensual",
        "moneda",
        "max_negocios",
        "max_tokens_mes",
        "activo",
    )
    list_filter = ("activo",)
    prepopulated_fields = {"codigo": ("nombre",)}


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ("cuenta", "plan", "estado", "proximo_cobro", "actualizada_el")
    list_filter = ("estado", "plan")
    search_fields = ("cuenta__nombre_comercial", "id_preaprobacion")
    readonly_fields = ("creada_el", "actualizada_el")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "suscripcion",
        "monto",
        "moneda",
        "estado",
        "id_externo",
        "pagado_el",
    )
    list_filter = ("estado", "proveedor")
    search_fields = ("id_externo",)
    date_hierarchy = "creado_el"


@admin.register(EventoPagoExterno)
class EventoPagoExternoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "proveedor", "procesado", "intentos", "recibido_el")
    list_filter = ("procesado", "proveedor", "tipo")
    search_fields = ("clave_idempotencia",)
    readonly_fields = (
        "proveedor",
        "tipo",
        "clave_idempotencia",
        "carga_util",
        "procesado",
        "intentos",
        "mensaje_error",
        "procesado_el",
        "recibido_el",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ConsumoIA)
class ConsumoIAAdmin(admin.ModelAdmin):
    list_display = (
        "cuenta",
        "periodo",
        "tokens_entrada",
        "tokens_salida",
        "llamadas",
    )
    list_filter = ("periodo",)
    readonly_fields = ("actualizado_el",)
