#!/usr/bin/env python3
"""
Consulta mensajes no impresos en Supabase, los imprime via USB (python-escpos)
y los marca como printed.
Orden seguro: imprimir → marcar. Si falla en el medio, se reintenta en el siguiente ciclo.

Instalación:
    pip install python-escpos

Encontrar VID/PID de tu impresora (Mac):
    system_profiler SPUSBDataType | grep -A5 "Printer\|POS\|Thermal"
  o bien:
    python3 -c "import usb.core; [print(hex(d.idVendor), hex(d.idProduct), d.manufacturer) for d in usb.core.find(find_all=True)]"
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

from escpos.printer import Usb

# ── Configura aquí tu impresora ───────────────────────────────────────────────
PRINTER_VENDOR_ID  = 0x0483   # XPrinter
PRINTER_PRODUCT_ID = 0x5743   # XPrinter
PRINTER_PROFILE    = "default"
# ─────────────────────────────────────────────────────────────────────────────

SUPABASE_URL      = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_ROLE_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}


def log(msg: str) -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def supabase_request(method: str, path: str, body: Optional[dict] = None) -> "list | dict":
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {e.read().decode()}") from e


def fetch_pending() -> list[dict]:
    path = "messages?printed=eq.false&order=created_at.asc&select=id,title,body"
    result = supabase_request("GET", path)
    return result if isinstance(result, list) else []


def mark_printed(message_id: str) -> None:
    supabase_request("PATCH", f"messages?id=eq.{message_id}", {"printed": True})


def print_message(msg: dict) -> None:
    p = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, profile=PRINTER_PROFILE)
    try:
        p.set(align="center", bold=True, height=2, width=2)
        p.textln(msg["title"])
        p.set(align="left", bold=False, height=1, width=1)
        p.ln()
        p.textln(msg["body"])
        p.ln(3)
        p.cut()
    finally:
        p.close()


def main() -> None:
    log("Consultando mensajes pendientes...")
    try:
        messages = fetch_pending()
    except Exception as e:
        log(f"ERROR al consultar Supabase: {e}")
        sys.exit(1)

    if not messages:
        log("Sin mensajes pendientes.")
        return

    log(f"Encontrados {len(messages)} mensajes.")

    success = 0
    for msg in messages:
        msg_id = msg["id"]
        try:
            log(f"Imprimiendo [{msg_id}]: {msg['title']!r}")
            print_message(msg)
            mark_printed(msg_id)
            log(f"OK [{msg_id}]")
            success += 1
        except Exception as e:
            log(f"FALLO [{msg_id}]: {e} — se reintentará en el siguiente ciclo")

    log(f"Ciclo completado: {success}/{len(messages)} impresos.")


if __name__ == "__main__":
    main()
