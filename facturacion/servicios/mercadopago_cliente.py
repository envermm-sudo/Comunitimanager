import logging
from datetime import timedelta
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

API_BASE = "https://api.mercadopago.com"
MINUTOS_VIGENCIA_QR = 30


def _headers():
    return {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _id_vendedor():
    token = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)
    if not token:
        return None
    return token.split("-")[-1]


def construir_referencia(cuenta_id, plan_id, modo):
    prefijo = getattr(settings, "PREFIJO_REFERENCIA", "CM")
    return f"{prefijo}_{cuenta_id}_{plan_id}_{modo}"


def parsear_referencia(referencia):
    if not referencia:
        return None
    partes = referencia.split("_")
    if len(partes) < 4:
        return None
    prefijo = getattr(settings, "PREFIJO_REFERENCIA", "CM")
    if partes[0] != prefijo:
        return None
    return {
        "cuenta_id": partes[1],
        "plan_id": partes[2],
        "modo": partes[3],
    }


def obtener_pos_id():
    url = f"{API_BASE}/pos"
    try:
        resp = requests.get(url, headers=_headers(), timeout=15)
        if resp.status_code != 200:
            logger.error(f"Error al obtener cajas de Mercado Pago. Codigo de estado: {resp.status_code}")
            return None
        
        pos_external_id = getattr(settings, "MERCADOPAGO_POS_EXTERNAL_ID", "CMWEB")
        results = resp.json().get("results", [])
        for caja in results:
            if caja.get("external_id") == pos_external_id:
                return caja.get("external_id")
        
        logger.error(f"No existe la caja con external_id {pos_external_id} en Mercado Pago")
        return None
    except Exception:
        logger.error("Error de conexion al buscar cajas en Mercado Pago", exc_info=True)
        return None


def crear_orden_qr(cuenta_id, plan, titulo=None):
    token = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)
    if not token:
        return {"ok": False, "error": "Falta configurar MERCADOPAGO_ACCESS_TOKEN"}

    vendedor = _id_vendedor()
    pos_id = obtener_pos_id()
    if vendedor is None or pos_id is None:
        return {"ok": False, "error": "No se pudo ubicar la caja de cobro en Mercado Pago"}

    referencia = construir_referencia(cuenta_id, plan.id, "qr")
    monto = float(plan.precio_mensual)
    nombre_titulo = titulo if titulo is not None else f"Suscripcion - {plan.nombre}"

    url = f"{API_BASE}/instore/orders/qr/seller/collectors/{vendedor}/pos/{pos_id}/qrs"

    datos = {
        "external_reference": referencia,
        "title": nombre_titulo,
        "description": "Pago de suscripcion",
        "expiration_date": (timezone.now() + timedelta(minutes=MINUTOS_VIGENCIA_QR)).isoformat(timespec="milliseconds"),
        "total_amount": monto,
        "items": [{
            "title": plan.nombre,
            "unit_price": monto,
            "quantity": 1,
            "unit_measure": "unit",
            "total_amount": monto,
        }],
    }

    url_publica = getattr(settings, "URL_PUBLICA", "")
    if url_publica:
        datos["notification_url"] = f"{url_publica}/facturacion/webhook/mercadopago/"

    try:
        resp = requests.put(url, headers=_headers(), json=datos, timeout=20)
        if resp.status_code in (200, 201):
            qr_data = resp.json().get("qr_data", "")
            if not qr_data:
                return {"ok": False, "error": "Mercado Pago no devolvio el codigo QR"}
            return {
                "ok": True,
                "qr_data": qr_data,
                "referencia": referencia,
                "vence_en_minutos": MINUTOS_VIGENCIA_QR,
            }
        else:
            logger.error(f"Mercado Pago rechazo la orden QR. Status: {resp.status_code}, Respuesta: {resp.text}")
            return {"ok": False, "error": "Mercado Pago rechazo la orden de cobro"}
    except Exception:
        logger.error("No se pudo conectar con Mercado Pago para crear orden QR", exc_info=True)
        return {"ok": False, "error": "No se pudo conectar con Mercado Pago"}


def crear_preferencia_tarjeta(cuenta_id, plan, url_exito, url_fallo, url_pendiente):
    token = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)
    if not token:
        return {"ok": False, "error": "Falta configurar MERCADOPAGO_ACCESS_TOKEN"}

    referencia = construir_referencia(cuenta_id, plan.id, "tarjeta")

    datos = {
        "items": [{
            "title": f"Suscripcion - {plan.nombre}",
            "quantity": 1,
            "currency_id": plan.moneda,
            "unit_price": float(plan.precio_mensual),
        }],
        "back_urls": {
            "success": url_exito,
            "failure": url_fallo,
            "pending": url_pendiente,
        },
        "external_reference": referencia,
    }

    url_publica = getattr(settings, "URL_PUBLICA", "")
    if url_publica:
        datos["notification_url"] = f"{url_publica}/facturacion/webhook/mercadopago/"
        datos["auto_return"] = "approved"

    try:
        resp = requests.post(f"{API_BASE}/checkout/preferences", headers=_headers(), json=datos, timeout=20)
        if resp.status_code in (200, 201):
            cuerpo = resp.json()
            init_point = cuerpo.get("init_point")
            if not init_point:
                return {"ok": False, "error": "Mercado Pago no devolvio el enlace de pago"}
            return {
                "ok": True,
                "init_point": init_point,
                "referencia": referencia,
                "preferencia_id": cuerpo.get("id"),
            }
        else:
            logger.error(f"Mercado Pago rechazo la preferencia. Status: {resp.status_code}, Respuesta: {resp.text}")
            return {"ok": False, "error": "Mercado Pago rechazo la preferencia de pago"}
    except Exception:
        logger.error("No se pudo conectar con Mercado Pago para crear preferencia de tarjeta", exc_info=True)
        return {"ok": False, "error": "No se pudo conectar con Mercado Pago"}


def obtener_pago(pago_id):
    try:
        resp = requests.get(API_BASE + "/v1/payments/" + str(pago_id), headers=_headers(), timeout=20)
        if resp.status_code == 200:
            return {"ok": True, "datos": resp.json()}
        else:
            logger.error("Codigo de estado %s al consultar pago", resp.status_code)
            return {"ok": False, "error": "No se pudo consultar el pago"}
    except Exception:
        logger.error("No se pudo conectar con Mercado Pago", exc_info=True)
        return {"ok": False, "error": "No se pudo conectar con Mercado Pago"}


def obtener_orden_comercial(orden_id):
    try:
        resp = requests.get(API_BASE + "/merchant_orders/" + str(orden_id), headers=_headers(), timeout=20)
        if resp.status_code == 200:
            return {"ok": True, "datos": resp.json()}
        else:
            logger.error("Codigo de estado %s al consultar orden", resp.status_code)
            return {"ok": False, "error": "No se pudo consultar la orden"}
    except Exception:
        logger.error("No se pudo conectar con Mercado Pago", exc_info=True)
        return {"ok": False, "error": "No se pudo conectar con Mercado Pago"}
