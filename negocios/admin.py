from django.contrib import admin
from .models import Negocio


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rubro", "estado", "creado_el")
    list_filter = ("estado", "rubro")
    search_fields = ("nombre", "rubro")
