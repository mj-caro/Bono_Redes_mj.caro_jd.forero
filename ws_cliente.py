# Importamos ssl porque la conexión con el servidor usa TLS.
import ssl

# Importamos websocket para crear y manejar la conexión WebSocket.
import websocket


# Creamos una clase para agrupar las funciones de conexión,envío, recepción y cierre.
class WSCliente:

    # Esta función se ejecuta automáticamente al crear un objeto WSCliente. "self" representa el objeto y "url" es la dirección del servidor.
    def __init__(self, url: str):

        # Creamos la conexión WebSocket con el servidor. create_connection realiza el handshake de WebSocket.
        self.ws = websocket.create_connection(
            url,

            # Configuramos las opciones de TLS.
            sslopt={
                # En este laboratorio no verificamos el certificado.
                "cert_reqs": ssl.CERT_NONE
            }
        )

    # Esta función envía datos al servidor.Los datos son bytes porque AlpesPay utiliza mensajes binarios.
    def send_bytes(self, data: bytes):

        # Enviamos los bytes como un mensaje WebSocket binario.
        self.ws.send(
            data,
            opcode=websocket.ABNF.OPCODE_BINARY
        )

    # Esta función recibe un mensaje del servidor.
    def recv_bytes(self) -> bytes:

        # Esperamos y recibimos el siguiente mensaje.
        data = self.ws.recv()

        # Si el servidor devuelve texto, lo convertimos a bytes.
        if isinstance(data, str):
            return data.encode()

        # Si ya son bytes, los devolvemos directamente.
        return data

    # Esta función cierra la conexión con el servidor.
    def close(self):

        # Cerramos la conexión WebSocket.
        self.ws.close()