from django.urls import path
from facturacion.vistas.webhook import webhook_mercadopago

app_name = "facturacion"

urlpatterns = [
    path("webhook/mercadopago/", webhook_mercadopago, name="webhook_mercadopago"),
]
