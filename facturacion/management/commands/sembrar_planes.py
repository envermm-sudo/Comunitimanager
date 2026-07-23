from django.core.management.base import BaseCommand
from facturacion.models import Plan


class Command(BaseCommand):
    help = "Carga o actualiza los planes comerciales"

    PLANES = [
        {
            "codigo": "inicial",
            "nombre": "Inicial",
            "descripcion": "Para un negocio que arranca",
            "precio_mensual": 0,
            "max_negocios": 1,
            "max_redes_por_negocio": 2,
            "max_publicaciones_mes": 15,
            "max_tokens_mes": 50000,
            "max_usuarios": 1,
            "orden": 1,
        },
        {
            "codigo": "profesional",
            "nombre": "Profesional",
            "descripcion": "Para un negocio en marcha",
            "precio_mensual": 0,
            "max_negocios": 1,
            "max_redes_por_negocio": 5,
            "max_publicaciones_mes": 60,
            "max_tokens_mes": 300000,
            "max_usuarios": 2,
            "orden": 2,
        },
        {
            "codigo": "agencia",
            "nombre": "Agencia",
            "descripcion": "Para quien administra varios negocios",
            "precio_mensual": 0,
            "max_negocios": 10,
            "max_redes_por_negocio": 5,
            "max_publicaciones_mes": 300,
            "max_tokens_mes": 1000000,
            "max_usuarios": 5,
            "orden": 3,
        },
    ]

    def handle(self, *args, **options):
        creados = 0
        existentes = 0
        for item in self.PLANES:
            datos = dict(item)
            codigo = datos.pop("codigo")
            _, created = Plan.objects.get_or_create(
                codigo=codigo,
                defaults=datos,
            )
            if created:
                creados += 1
            else:
                existentes += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Planes listos. Creados: {creados}, ya existentes sin modificar: {existentes}"
            )
        )
