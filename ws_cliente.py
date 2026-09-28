# Importamos ssl porque la conexión con el servidor usa TLS.
import ssl

# Importamos la librería websocket, para crear una conexión WebSocket sin tener que programar todo el protocolo WebSocket desde cero.
import websocket

# Creamos una clase llamada WSCliente para tener en un solo lugar todas las funciones necesarias para conectarnos, enviar, recibir y cerrar.
class WSCliente:

    # __init__ se ejecuta automáticamente cuando creamos un objeto de la clase y "self" representa al objeto que vamos a crear y "url" es la dirección del servidor al que nos vamos a conectar.
    def __init__(self, url: str):

        # Acá creamos la conexión WebSocket usando la URL recibida y pues create_connection se encarga de realizar el handshake  y asi establecer la conexión.
        self.ws = websocket.create_connection(
            url,
            sslopt={ # sslopt tiene opciones relacionadas con TLS/SSL.

                # Para que no haya problema si el sistema no reconoce como un certificado pues ponemos que no lo verifique y ya
                "cert_reqs": ssl.CERT_NONE
            }
        )

    # Esta función es para enviar datos al servidor. "data" va a ser un objeto de tipo bytes porque dice que alpespay tiene protocolo binario
    def send_bytes(self, data: bytes):

        # Enviamos los datos por WebSocket diciendo que sonun mensaje binario y no un mensaje de texto.
        self.ws.send(
            data,
            opcode=websocket.ABNF.OPCODE_BINARY
        )

    #Esta lo que hace es recibir un mensaje enviado por el servidor.
    def recv_bytes(self) -> bytes:

        # Esperamos y recibimos el siguiente mensaje del servidor.
        data = self.ws.recv()

        # Si en algun momento el servidor devuelve texto,lo convertimos a bytes para que no tengamos ningun problema con eso.
        if isinstance(data, str):
            return data.encode()

        # Y pues si ya recibimos bytes, los devolvemos directamente obvio
        return data

    # Aca cerramos la conexión con el servidor.
    def close(self):

        # Cerramos la conexión WebSocket.
        self.ws.close()