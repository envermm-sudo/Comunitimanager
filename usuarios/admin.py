from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("email", "nombre", "apellido")


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ("email", "nombre", "apellido")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    list_display = ("email", "nombre", "apellido", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "nombre", "apellido")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("nombre", "apellido")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "fecha_alta")}),
    )

    readonly_fields = ("fecha_alta", "last_login")

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "nombre", "apellido", "password1", "password2")}),
    )
