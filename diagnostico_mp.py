import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not TOKEN:
    raise SystemExit("Falta MERCADOPAGO_ACCESS_TOKEN en el archivo .env")

HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Content-Type": "application/json",
}


def listar():
    resp = requests.get("https://api.mercadopago.com/pos", headers=HEADERS)
    print("Estado HTTP:", resp.status_code)
    if resp.status_code != 200:
        print(resp.text)
        return
    cajas = resp.json().get("results", [])
    if not cajas:
        print("No hay ninguna caja creada en esta cuenta.")
        return
    for caja in cajas:
        print("-" * 40)
        print("id interno :", caja.get("id"))
        print("nombre     :", caja.get("name"))
        print("external_id:", caja.get("external_id"))


def asignar(caja_id, externo):
    url = "https://api.mercadopago.com/pos/" + str(caja_id)
    resp = requests.put(url, headers=HEADERS, json={"external_id": externo})
    print("Estado HTTP:", resp.status_code)
    if resp.status_code in (200, 201):
        print("Listo. external_id asignado:", resp.json().get("external_id"))
    else:
        print(resp.text)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        listar()
    elif len(sys.argv) == 3:
        asignar(sys.argv[1], sys.argv[2])
    else:
        print("Uso:")
        print("  python diagnostico_mp.py")
        print("  python diagnostico_mp.py <id> <externo>")