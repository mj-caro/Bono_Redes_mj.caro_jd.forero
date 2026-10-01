import struct
import sys

from ws_cliente import WSCliente


def hexdump(b: bytes) -> str:
    # Mostramos los bytes en hexadecimal para poder comparar
    # lo que mandamos con lo que vimos en Wireshark.
    return " ".join(f"{x:02x}" for x in b)


def construir_mensaje(tipo: int, datos: bytes) -> bytes:
    # "AC" identifica el servicio de cuentas.
    servicio = b"AC"

    # Las banderas por ahora van en 0.
    banderas = 0

    # ">BBH" = tipo (1 byte) + banderas (1 byte) + longitud (2 bytes)
    cabecera = struct.pack(">BBH", tipo, banderas, len(datos))

    # Juntamos todas las partes del mensaje.
    return servicio + cabecera + datos


def construir_login(usuario: str, pin: str) -> bytes:
    # Convertimos el usuario a bytes.
    usuario_bytes = usuario.encode()

    # Convertimos el PIN a bytes.
    pin_bytes = pin.encode()

    # En Wireshark vimos que hay un byte 00
    # entre el usuario y el PIN.
    datos = usuario_bytes + b"\x00" + pin_bytes

    # La operación 02 corresponde al login.
    return construir_mensaje(2, datos)


def obtener_token(respuesta: bytes) -> bytes:
    # Revisamos que la respuesta tenga al menos la cabecera.
    if len(respuesta) < 6:
        raise ValueError("La respuesta de login es demasiado corta.")

    # El tercer byte muestraaa el tipo de respuesta.
    tipo = respuesta[2]

    # La respuesta correcta al login es 82.
    if tipo != 0x82:
        raise ValueError(
            f"El login no fue aceptado. "
            f"El servidor respondió con tipo {tipo:02x}."
        )

    # Los datos empiezan después de la cabecera de 6 bytes.
    datos = respuesta[6:]

    # El token ocupa 4 bytes.
    token = datos[:4]

    return token


def construir_consulta_saldo(token: bytes) -> bytes:
    # La operación 03 corresponde a consultar el saldo.
    return construir_mensaje(3, token)


def obtener_saldo(respuesta: bytes) -> int:
    # Revisamos que la respuesta tenga al menos la cabecera.
    # La cabecera mide 6 bytes: servicio (2) + tipo (1) + banderas (1) + longitud (2).
    if len(respuesta) < 6:
        raise ValueError("La respuesta de saldo es demasiado corta.")

    # El tercer byte indica el tipo de respuesta.
    tipo = respuesta[2]

    # Si el servidor respondió con error (ee), mostramos el mensaje.
    if tipo == 0xEE:
        raise ValueError(
            f"El servidor devolvió un error: "
            f"{respuesta[7:].decode(errors='replace')}"
        )

    # La respuesta correcta al saldo es 83.
    if tipo != 0x83:
        raise ValueError(
            f"La consulta de saldo falló. "
            f"El servidor respondió con tipo {tipo:02x}."
        )

    # Los datos empiezan después de la cabecera de 6 bytes.
    datos = respuesta[6:]

    # En la captura vimos que el saldo ocupa 8 bytes.
    if len(datos) != 8:
        raise ValueError("El saldo no tiene 8 bytes.")

    # Convertimos los 8 bytes a un número entero.
    # ">Q" esto significa: big-endian, entero sin signo de 8 bytes.
    saldo_centavos = struct.unpack(">Q", datos)[0]

    # Devolvemos el saldo en centavos.
    return saldo_centavos

def main(url: str) -> None:
    # Creamos la conexión con el servidor.
    c = WSCliente(url)

    print("conectado a", url, "— el canal WebSocket está listo.")

    try:

        # ---------------------------------------------------------
        # 1. ANUNCIO
        # ---------------------------------------------------------

        # Texto que vimos en la captura.
        datos_inicio = b"alpespay-web"

        # La operación 01 corresponde al anuncio.
        mensaje_inicio = construir_mensaje(1, datos_inicio)

        print("-> anuncio:", hexdump(mensaje_inicio))

        # Enviamos el anuncio.
        c.send_bytes(mensaje_inicio)

        # Recibimos la respuesta.
        respuesta_inicio = c.recv_bytes()

        print("<- respuesta anuncio:", hexdump(respuesta_inicio))


        # ---------------------------------------------------------
        # 2. LOGIN
        # ---------------------------------------------------------

        # Usuario utilizado en la captura.
        usuario = "equipo34"

        # PIN utilizado en la captura.
        pin = "9672"

        # Construimos el mensaje de login.
        mensaje_login = construir_login(usuario, pin)

        print("-> login:", hexdump(mensaje_login))

        # Enviamos el login.
        c.send_bytes(mensaje_login)

        # Recibimos la respuesta del servidor.
        respuesta_login = c.recv_bytes()

        print("<- respuesta login:", hexdump(respuesta_login))

        # Intentamos obtener el token.
        token = obtener_token(respuesta_login)

        print("token:", hexdump(token))


        # ---------------------------------------------------------
        # 3. CONSULTA DE SALDO
        # ---------------------------------------------------------

        # Construimos la consulta usando el token.
        mensaje_saldo = construir_consulta_saldo(token)

        print("-> saldo:", hexdump(mensaje_saldo))

        # Enviamos la consulta.
        c.send_bytes(mensaje_saldo)

        # Recibimos la respuesta.
        respuesta_saldo = c.recv_bytes()

        print("<- respuesta saldo:", hexdump(respuesta_saldo))

        # Sacamos el saldo en centavos.
        saldo_centavos = obtener_saldo(respuesta_saldo)

        # Lo convertimos a unidades normales.
        saldo = saldo_centavos / 100

        print("saldo:", saldo)


    finally:
        # Cerramos la conexión.
        c.close()


if __name__ == "__main__":

    # Revisamos que se haya pasado la URL.
    if len(sys.argv) != 2:
        print("uso: python3 plantilla_cliente.py wss://<HOST>:<PUERTO>/")
        raise SystemExit(2)

    # Ejecutamos el programa.
    main(sys.argv[1])