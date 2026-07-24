import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from facturacion.models import EventoPagoExterno

logger = logging.getLogger(__name__)


def extraer_datos(request):
    """
    Devuelve una tupla de dos elementos: (tipo, identificador)
    Ambos pueden ser None.
    """
    tipo = request.GET.get("topic") or request.GET.get("type")
    identificador = request.GET.get("data.id") or request.GET.get("id")

    if request.body:
        try:
            cuerpo = json.loads(request.body)
            if tipo is None:
                tipo = cuerpo.get("topic") or cuerpo.get("type")
            if identificador is None:
                data = cuerpo.get("data")
                if isinstance(data, dict):
                    identificador = data.get("id")
                if identificador is None and cuerpo.get("resource"):
                    identificador = cuerpo["resource"].rstrip("/").split("/")[-1]
                if identificador is None:
                    identificador = cuerpo.get("id")
        except Exception:
            pass

    return (tipo, identificador)


def leer_cuerpo(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {
            "cuerpo_no_json": request.body.decode(errors="replace")[:2000]
        }


# Este webhook siempre responde 200 aunque el aviso sea desconocido o duplicado,
# porque Mercado Pago reintenta indefinidamente cuando recibe un codigo de error.
# El unico caso que devuelve 500 es cuando falla el guardado, para que Mercado Pago
# reintente y no se pierda el aviso.
@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    tipo, identificador = extraer_datos(request)

    if tipo is None or identificador is None:
        logger.warning("Llego un aviso incompleto de Mercado Pago")
        return HttpResponse(status=200)

    clave = "mercadopago:" + str(tipo) + ":" + str(identificador)

    carga = {
        "tipo": tipo,
        "identificador": str(identificador),
        "parametros": dict(request.GET),
        "cuerpo": leer_cuerpo(request),
    }

    try:
        evento, creado = EventoPagoExterno.objects.get_or_create(
            clave_idempotencia=clave,
            defaults={
                "proveedor": "mercadopago",
                "tipo": tipo,
                "carga_util": carga,
            },
        )
        if creado:
            logger.info("Aviso de Mercado Pago recibido: %s", clave)
        else:
            logger.info("Aviso de Mercado Pago duplicado, se ignora: %s", clave)
    except Exception:
        logger.error("Error al guardar aviso de Mercado Pago", exc_info=True)
        return HttpResponse(status=500)

    return HttpResponse(status=200)
