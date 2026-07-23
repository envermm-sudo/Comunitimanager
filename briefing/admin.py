from django.contrib import admin
from .models import Briefing, HechoBriefing


class HechoBriefingInline(admin.TabularInline):
    model = HechoBriefing
    extra = 0


@admin.register(Briefing)
class BriefingAdmin(admin.ModelAdmin):
    inlines = (HechoBriefingInline,)
    list_display = ("negocio", "completitud", "actualizado_el")


@admin.register(HechoBriefing)
class HechoBriefingAdmin(admin.ModelAdmin):
    list_display = ("briefing", "categoria", "clave", "origen", "confirmado")
    list_filter = ("categoria", "origen", "confirmado")
    search_fields = ("clave", "valor")
