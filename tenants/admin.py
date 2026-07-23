from django.contrib import admin
from .models import Cuenta, Dominio


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("nombre_comercial", "schema_name", "estado", "creado_el")


@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
