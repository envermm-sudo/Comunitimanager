from django.contrib import admin
from .models import Estrategia, PilarContenido, RitmoPublicacion


class PilarContenidoInline(admin.TabularInline):
    model = PilarContenido
    extra = 0


class RitmoPublicacionInline(admin.TabularInline):
    model = RitmoPublicacion
    extra = 0


@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    inlines = (PilarContenidoInline, RitmoPublicacionInline)
    list_display = (
        "negocio",
        "version",
        "estado",
        "periodo_desde",
        "periodo_hasta",
    )
    list_filter = ("estado",)
