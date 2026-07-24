import calendar
import logging
from datetime import date
from django.db import transaction
from django.utils import timezone
from facturacion.models import Plan, Suscripcion, Pago, EventoPagoExterno
from facturacion.servicios.mercadopago_cliente import (
    parsear_referencia,
    obtener_pago,
    obtener_orden_comercial,
)

logger = logging.getLogger(__name__)

MAX_INTENTOS = 10

ESTADOS_MP = {
    "approved": "aprobado",
    "rejected": "rechazado",
    "cancelled": "rechazado",
    "refunded": "devuelto",
    "charged_back": "devuelto",
}


def sumar_un_mes(fecha):
    if fecha.month == 12:
        anio = fecha.year + 1
        mes = 1
    else:
        anio = fecha.year
        mes = fecha.month + 1
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(fecha.day, ultimo_dia))


def traducir_estado(estado_mp):
    return ESTADOS_MP.get(estado_mp, "pendiente")


def extraer_pago_de_orden(orden):
    for pago in orden.get("payments", []):
        if pago.get("status") == "approved":
            return pago
    return None


def avanzar_suscripcion(suscripcion, plan, pago):
    hoy = timezone.localdate()
    if suscripcion.proximo_cobro is not None and suscripcion.proximo_cobro > hoy:
        base = suscripcion.proximo_cobro
    else:
        base = hoy
    nuevo_vencimiento = sumar_un_mes(base)

    pago.periodo_desde = base
    pago.periodo_hasta = nuevo_vencimiento
    pago.save(update_fields=["periodo_desde", "periodo_hasta"])

    suscripcion.plan = plan
    suscripcion.proximo_cobro = nuevo_vencimiento
    suscripcion.estado = "activa"
    suscripcion.fin_prueba = None
    suscripcion.cancelada_el = None
    suscripcion.save(update_fields=["plan", "proximo_cobro", "estado", "fin_prueba", "cancelada_el"])
    
    # Si la suscripcion todavia esta al dia, el nuevo vencimiento se calcula
    # desde la fecha de vencimiento anterior para no quitarle dias ya pagados
    # al cliente, y si esta vencida se calcula desde hoy.
    
    return nuevo_vencimiento


def registrar_pago(suscripcion, datos_pago):
    id_externo = str(datos_pago.get("id"))
    estado = traducir_estado(datos_pago.get("status"))
    monto = datos_pago.get("transaction_amount") or 0
    medio = datos_pago.get("payment_method_id") or ""

    pago, creado = Pago.objects.get_or_create(
        proveedor="mercadopago",
        id_externo=id_externo,
        defaults={
            "suscripcion": suscripcion,
            "monto": monto,
            "moneda": datos_pago.get("currency_id") or "ARS",
            "estado": estado,
            "medio_pago": medio,
            "pagado_el": timezone.now() if estado == "aprobado" else None,
        },
    )
    return (pago, creado)


def procesar_evento(evento):
    if evento.procesado:
        return {"ok": True, "detalle": "ya estaba procesado"}

    evento.intentos = evento.intentos + 1
    evento.save(update_fields=["intentos"])

    if evento.intentos > MAX_INTENTOS:
        evento.procesado = True
        evento.mensaje_error = "Se supero el maximo de intentos"
        evento.procesado_el = timezone.now()
        evento.save(update_fields=["procesado", "mensaje_error", "procesado_el"])
        return {"ok": False, "detalle": "maximo de intentos superado"}

    identificador = evento.carga_util.get("identificador")
    if not identificador:
        evento.procesado = True
        evento.mensaje_error = "El aviso no trae identificador"
        evento.procesado_el = timezone.now()
        evento.save(update_fields=["procesado", "mensaje_error", "procesado_el"])
        return {"ok": False, "detalle": "sin identificador"}

    if evento.tipo == "payment":
        respuesta = obtener_pago(identificador)
        if not respuesta.get("ok"):
            evento.mensaje_error = respuesta.get("error", "")
            evento.save(update_fields=["mensaje_error"])
            return {"ok": False, "detalle": "no se pudo consultar el pago"}
        datos_pago = respuesta["datos"]
    elif evento.tipo == "merchant_order":
        respuesta = obtener_orden_comercial(identificador)
        if not respuesta.get("ok"):
            evento.mensaje_error = respuesta.get("error", "")
            evento.save(update_fields=["mensaje_error"])
            return {"ok": False, "detalle": "no se pudo consultar la orden"}
        orden = respuesta["datos"]
        datos_pago = extraer_pago_de_orden(orden)
        if datos_pago is None:
            evento.mensaje_error = "La orden todavia no tiene un pago aprobado"
            evento.save(update_fields=["mensaje_error"])
            return {"ok": False, "detalle": "orden sin pago aprobado"}
        if "external_reference" not in datos_pago:
            datos_pago["external_reference"] = orden.get("external_reference")
    else:
        evento.procesado = True
        evento.mensaje_error = "Tipo de aviso no manejado"
        evento.procesado_el = timezone.now()
        evento.save(update_fields=["procesado", "mensaje_error", "procesado_el"])
        return {"ok": True, "detalle": "tipo no manejado, se descarta"}

    referencia = datos_pago.get("external_reference")
    datos_referencia = parsear_referencia(referencia)

    if datos_referencia is None:
        evento.procesado = True
        evento.mensaje_error = "La referencia no pertenece a este sistema"
        evento.procesado_el = timezone.now()
        evento.save(update_fields=["procesado", "mensaje_error", "procesado_el"])
        return {"ok": True, "detalle": "referencia ajena, se descarta"}

    suscripcion = Suscripcion.objects.filter(
        cuenta_id=datos_referencia["cuenta_id"]
    ).first()
    plan = Plan.objects.filter(id=datos_referencia["plan_id"]).first()

    if suscripcion is None or plan is None:
        evento.mensaje_error = "No se encontro la suscripcion o el plan del aviso"
        evento.save(update_fields=["mensaje_error"])
        return {"ok": False, "detalle": "suscripcion o plan inexistente"}

    estado = traducir_estado(datos_pago.get("status"))

    if estado == "pendiente":
        evento.mensaje_error = "El pago todavia esta pendiente en Mercado Pago"
        evento.save(update_fields=["mensaje_error"])
        return {"ok": False, "detalle": "pago pendiente"}

    with transaction.atomic():
        pago, creado = registrar_pago(suscripcion, datos_pago)
        
        # La suscripcion solo se avanza cuando el pago es nuevo, es decir cuando get_or_create lo creo.
        # Si el mismo pago llega dos veces por avisos distintos, el segundo no suma tiempo.
        
        if estado == "aprobado" and creado:
            nuevo_vencimiento = avanzar_suscripcion(suscripcion, plan, pago)
            detalle = "pago aprobado, vencimiento nuevo " + str(nuevo_vencimiento)
        elif estado == "aprobado" and not creado:
            detalle = "pago aprobado ya registrado, no se vuelve a sumar tiempo"
        else:
            detalle = "pago con estado " + estado

        evento.procesado = True
        evento.mensaje_error = ""
        evento.procesado_el = timezone.now()
        evento.save(update_fields=["procesado", "mensaje_error", "procesado_el"])

    logger.info("Evento procesado: %s | %s", evento.clave_idempotencia, detalle)
    return {"ok": True, "detalle": detalle}


def procesar_pendientes(limite=50):
    eventos = EventoPagoExterno.objects.filter(procesado=False).order_by("recibido_el")[:limite]
    procesados = 0
    fallidos = 0
    total = 0
    for evento in eventos:
        total += 1
        try:
            resultado = procesar_evento(evento)
        except Exception:
            logger.error(
                "Error inesperado procesando el evento %s",
                evento.clave_idempotencia,
                exc_info=True,
            )
            resultado = {"ok": False, "detalle": "error inesperado"}
        if resultado.get("ok"):
            procesados += 1
        else:
            fallidos += 1
    return {"procesados": procesados, "fallidos": fallidos, "total": total}