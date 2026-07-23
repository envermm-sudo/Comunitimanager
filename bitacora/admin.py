from django.contrib import admin
from bitacora.models import EventoBitacora


@admin.register(EventoBitacora)
class EventoBitacoraAdmin(admin.ModelAdmin):
    list_display = (
        "creado_el",
        "negocio",
        "tipo_actor",
        "actor",
        "accion",
        "resultado",
    )
    list_filter = (
        "tipo_actor",
        "resultado",
        "accion",
    )
    search_fields = (
        "accion",
        "objeto_id",
    )
    date_hierarchy = "creado_el"

    readonly_fields = (
        "negocio",
        "tipo_actor",
        "actor",
        "accion",
        "objeto_tipo",
        "objeto_id",
        "detalle",
        "resultado",
        "mensaje_error",
        "direccion_ip",
        "creado_el",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
