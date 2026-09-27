"""
plantilla_cliente.py — ESQUELETO para TU cliente de AlpesPay.

La capa de transporte ya está resuelta: `ws_cliente.py` (que va junto a este
archivo) implementa WebSocket sobre TLS — handshake, framing y máscara — y te da
un canal para enviar y recibir BYTES:

    c = WSCliente("wss://<HOST>:<PUERTO>/")
    c.send_bytes(b"...")          # envías bytes
    respuesta = c.recv_bytes()    # recibes bytes (un mensaje)
    c.close()

Tu trabajo es implementar el PROTOCOLO: qué bytes mandar y cómo leer las
respuestas. Eso lo reconstruyes tú a partir de TU captura (Wireshark, filtro de
visualización `websocket`). Este archivo NO trae la solución: los identificadores
de servicio y de operación, los tamaños/orden de los campos y la firma los
deduces del tráfico.

No estás obligado a usar `ws_cliente.py`: puedes usar la librería que prefieras
(p. ej. `websocket-client`) o implementar tú mismo el handshake/framing sobre un
socket TLS. Lo único fijo es que se habla WebSocket sobre TLS.

Uso:
    python3 plantilla_cliente.py wss://<HOST>:<PUERTO>/
(HOST y PUERTO los ves en tu captura.)

Descifrado de TU propio tráfico: usa un Python con OpenSSL 1.1.1+ (no el LibreSSL
de fábrica de macOS) y define SSLKEYLOGFILE antes de ejecutar; `ws_cliente.py`
exporta las claves para Wireshark. Ver el manual (Subsistema de captura).
"""

import struct  # empacar/desempacar enteros; el protocolo es big-endian -> usa ">"
import sys

from ws_cliente import WSCliente


def hexdump(b: bytes) -> str:
    """Bytes -> 'aa bb cc ...' para inspeccionar respuestas mientras experimentas."""
    return " ".join(f"{x:02x}" for x in b)


def main(url: str) -> None:
    c = WSCliente(url)
    print("conectado a", url, "— el canal WebSocket está listo.")
    try:
        # ─────────────────────────────────────────────────────────────────────
        # A PARTIR DE AQUÍ ES TU CLIENTE. El canal ya envía/recibe BYTES crudos:
        #
        #     c.send_bytes( <tus bytes> )
        #     resp = c.recv_bytes()
        #     print("<-", hexdump(resp))
        #
        # Método (pistas de CÓMO, no de la respuesta):
        #   • Observa en tu captura los primeros bytes de cada mensaje: identifican
        #     a qué servicio va dirigido.
        #   • Empaca/lee enteros con struct en big-endian:
        #         struct.pack(">I", n)      # entero de 4 bytes
        #         struct.unpack(">q", buf)  # entero de 8 bytes con signo
        #   • Empieza por el mensaje más corto y repetido y alinéalo byte a byte.
        #   • El identificador de sesión (token) que te devuelven acompaña, sin
        #     cambios, a las peticiones siguientes.
        #
        # TODO 1: anúnciate / inicia sesión con tu usuario y PIN; guarda el token.
        # TODO 2: consulta tu saldo.
        # TODO 3: el resto del protocolo lo descubres tú a partir de la captura.
        # ─────────────────────────────────────────────────────────────────────
        raise SystemExit("Aún no envías nada: completa los TODO de este archivo.")
    finally:
        c.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python3 plantilla_cliente.py wss://<HOST>:<PUERTO>/")
        raise SystemExit(2)
    main(sys.argv[1])
