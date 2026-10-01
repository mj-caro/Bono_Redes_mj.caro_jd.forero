# Importamos ssl porque la conexión con el servidor usa TLS.
import ssl

# Importamos la versión síncrona de websockets para manejar la conexión.
from websockets.sync.client import connect


# Creamos una clase para manejar la conexión con el servidor.
class WSCliente:

    # Esta función se ejecuta cuando creamos un objeto WSCliente.
    def __init__(self, url: str):

        # Creamos un contexto TLS.
        contexto = ssl.create_default_context()

        # En este laboratorio no verificamos el certificado.
        contexto.check_hostname = False
        contexto.verify_mode = ssl.CERT_NONE

        # Creamos la conexión WebSocket.
        self.ws = connect(
            url,

            # Usamos el mismo origen que aparece en la captura del navegador.
            origin="https://alpespay.datoid.co",

            # Permitimos la compresión WebSocket que usa el navegador.
            compression="deflate",

            # Usamos nuestro contexto TLS.
            ssl_context=contexto
        )

    # Esta función envía datos binarios al servidor.
    def send_bytes(self, data: bytes):

        # Enviamos los bytes como mensaje binario.
        self.ws.send(data)

    # Esta función recibe un mensaje del servidor.
    def recv_bytes(self) -> bytes:

        # Esperamos la respuesta del servidor.
        data = self.ws.recv()

        # Si llega como texto, lo convertimos a bytes.
        if isinstance(data, str):
            return data.encode()

        # Si ya son bytes, los devolvemos directamente.
        return data

    # Esta función cierra la conexión.
    def close(self):

        # Cerramos el WebSocket.
        self.ws.close()