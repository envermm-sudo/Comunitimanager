from django.core.management.base import BaseCommand
from facturacion.servicios.procesador_pagos import procesar_pendientes


class Command(BaseCommand):
    help = "Procesa los avisos de pago recibidos y todavia no resueltos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limite",
            type=int,
            default=50,
            help="Cantidad maxima de avisos a procesar",
        )

    def handle(self, *args, **options):
        resultado = procesar_pendientes(limite=options["limite"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Procesamiento finalizado. Total revisado: {resultado['total']}, Procesados: {resultado['procesados']}, Fallidos: {resultado['fallidos']}"
            )
        )
