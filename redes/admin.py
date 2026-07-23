from django.contrib import admin
from .models import RedConectada, CredencialOAuth


@admin.register(RedConectada)
class RedConectadaAdmin(admin.ModelAdmin):
    list_display = ("negocio", "plataforma", "nombre_externo", "estado", "conectada_el")
    list_filter = ("plataforma", "estado")
    search_fields = ("nombre_externo", "id_externo")


@admin.register(CredencialOAuth)
class CredencialOAuthAdmin(admin.ModelAdmin):
    list_display = ("red", "estado", "vence_el", "ultimo_refresco")
    list_filter = ("estado",)
    readonly_fields = ("creada_el", "actualizada_el")
    exclude = ("token_acceso", "token_refresco")
