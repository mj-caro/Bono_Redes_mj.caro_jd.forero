import struct
import sys

from ws_cliente import WSCliente


def hexdump(b: bytes) -> str:
    """Bytes -> 'aa bb cc ...' para inspeccionar respuestas."""
    return " ".join(f"{x:02x}" for x in b)


def construir_mensaje(tipo: int, datos: bytes) -> bytes:
    # "AC" identifica el protocolo de AlpesPay.
    cabecera = b"AC"

    # El tipo identifica la operación.
    tipo_bytes = struct.pack(">B", tipo)

    # Calculamos el tamaño de los datos.
    longitud = len(datos)

    # Guardamos la longitud en 4 bytes, big-endian.
    longitud_bytes = struct.pack(">I", longitud)

    # Unimos todas las partes del mensaje.
    return cabecera + tipo_bytes + longitud_bytes + datos


def main(url: str) -> None:
    # Creamos la conexión con el servidor.
    c = WSCliente(url)

    print("conectado a", url, "— el canal WebSocket está listo.")

    try:
        # Datos observados en el primer mensaje de la captura.
        datos_inicio = b"alpespay-web"

        # Construimos el mensaje inicial.
        mensaje_inicio = construir_mensaje(1, datos_inicio)

        # Mostramos lo que vamos a enviar.
        print("->", hexdump(mensaje_inicio))

        # Enviamos el mensaje.
        c.send_bytes(mensaje_inicio)

        # Recibimos la respuesta.
        respuesta = c.recv_bytes()

        # Mostramos la respuesta.
        print("<-", hexdump(respuesta))

    finally:
        # Cerramos la conexión.
        c.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python3 plantilla_cliente.py wss://<HOST>:<PUERTO>/")
        raise SystemExit(2)

    main(sys.argv[1])