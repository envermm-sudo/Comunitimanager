from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("facturacion/", include("facturacion.urls")),
    path("admin/", admin.site.urls),
]
