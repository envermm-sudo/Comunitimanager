from django.core.management.base import BaseCommand
from facturacion.models import MedioPago


class Command(BaseCommand):
    help = "Carga los medios de pago iniciales"

    MEDIOS = [
        {
            "codigo": "qr",
            "nombre": "Codigo QR",
            "descripcion": "Pagas escaneando con la app de Mercado Pago",
            "modo": "qr",
            "instrucciones": "Escanea el codigo con la aplicacion de Mercado Pago desde tu telefono. La acreditacion es inmediata.",
            "requiere_comprobante": False,
            "requiere_aprobacion_manual": False,
            "orden": 1,
        },
        {
            "codigo": "tarjeta",
            "nombre": "Tarjeta",
            "descripcion": "Pagas con tarjeta a traves de Mercado Pago",
            "modo": "tarjeta",
            "instrucciones": "Vas a ser dirigido al sitio seguro de Mercado Pago para completar el pago con tu tarjeta.",
            "requiere_comprobante": False,
            "requiere_aprobacion_manual": False,
            "orden": 2,
        },
        {
            "codigo": "transferencia",
            "nombre": "Transferencia bancaria",
            "descripcion": "Transferis y nos envias el comprobante",
            "modo": "transferencia",
            "instrucciones": "Realiza la transferencia y adjunta el comprobante. La activacion se realiza luego de verificar el pago.",
            "requiere_comprobante": True,
            "requiere_aprobacion_manual": True,
            "orden": 3,
        },
        {
            "codigo": "gratis",
            "nombre": "Sin costo",
            "descripcion": "Para planes de valor cero",
            "modo": "gratis",
            "instrucciones": "Este plan no tiene costo. La activacion es inmediata.",
            "requiere_comprobante": False,
            "requiere_aprobacion_manual": False,
            "orden": 4,
        },
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0
        for item in self.MEDIOS:
            datos = dict(item)
            codigo = datos.pop("codigo")
            _, created = MedioPago.objects.get_or_create(
                codigo=codigo,
                defaults=datos,
            )
            if created:
                creados += 1
            else:
                existentes += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Medios de pago listos. Creados: {creados}, ya existentes sin modificar: {existentes}"
            )
        )
