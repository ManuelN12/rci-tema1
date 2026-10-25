"""Práctica 0: servidor TCP que envía una trama con la edad, el DNI y la altura.

Hace el papel del robot en las prácticas del UR3e: espera a que se conecte un
cliente y, sin que este pida nada, le envía una trama por segundo.

Formato de cada trama (todo en big-endian, como la interfaz primaria del UR):

- Cabecera de 5 bytes: ``int32 messageSize`` (incluye la cabecera) +
  ``uint8 messageType`` (1 = datos personales).
- Contenido de 9 bytes: ``uint8`` edad + ``uint32`` DNI + ``float32`` altura (m).

Se lanza desde VS Code (F5). Los datos se cambian en la configuración de abajo.
"""
import socket
import struct
import sys
from time import sleep

# ------------------------------------------------------------------ configuración
HOST = "127.0.0.1"  # "0.0.0.0" para aceptar conexiones de otros PC (ampliación)
PORT = 50000
EDAD = 22  # años (0-255)
DNI = 12345678  # número del DNI, sin letra
ALTURA = 1.75  # metros
VECES = 100  # tramas que se envían antes de cerrar
PERIODO = 1.0  # segundos entre tramas
# --------------------------------------------------------------------------------


class PersonaServer:
    """Servidor TCP que envía periódicamente una trama con datos personales."""

    MESSAGE_TYPE_PERSONA = 1
    HEADER_FORMAT = ">iB"  # messageSize, messageType
    PERSONA_FORMAT = ">BIf"  # edad, dni, altura
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    PERSONA_SIZE = struct.calcsize(PERSONA_FORMAT)

    def __init__(self, host: str = "127.0.0.1", port: int = 50000) -> None:
        self.host = host
        self.port = port
        self.sock_escucha = None

    def listen(self) -> "PersonaServer":
        """Reserva el puerto y se pone a la escucha de conexiones."""
        self.sock_escucha = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un enchufe de red IPv4 (AF_INET) y TCP (SOCK_STREAM)
        if sys.platform != "win32":  # relanzar sin esperar (en Windows cambia de sentido)
            self.sock_escucha.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_escucha.bind((self.host, self.port))#Reserva el puerto 5000 para este programa
        self.sock_escucha.listen(1)# Se pone a escuchar. Desde aquí el sistema operativo acepta conexiones
        return self

    def build_message(self, edad: int, dni: int, altura: float) -> bytes:
        """Construye la trama completa: cabecera + contenido."""
        contenido = struct.pack(self.PERSONA_FORMAT, edad, dni, altura)
        cabecera = struct.pack(self.HEADER_FORMAT, self.HEADER_SIZE + len(contenido),
                               self.MESSAGE_TYPE_PERSONA)
        return cabecera + contenido

    def serve_one_client(self, mensaje: bytes, veces: int, periodo: float) -> None:
        """Espera a un cliente y le envía ``mensaje`` ``veces`` veces."""
        print(f"Esperando un cliente en {self.host}:{self.port} ...")
        conexion, direccion = self.sock_escucha.accept()# accept() Se queda parado el programa ahi hasta que alguien se conecte
        print(f"Cliente conectado desde {direccion[0]}:{direccion[1]}")
        with conexion:
            for i in range(veces):
                conexion.sendall(mensaje)
                print(f"Trama {i + 1} enviada ({len(mensaje)} B): {mensaje.hex(' ')}")
                sleep(periodo)
        print("Conexión cerrada")

    def close(self) -> None:
        if self.sock_escucha is not None:
            self.sock_escucha.close()
            self.sock_escucha = None


def main() -> None:
    servidor = PersonaServer(host=HOST, port=PORT)
    try:
        mensaje = servidor.build_message(EDAD, DNI, ALTURA)
        servidor.listen()
        servidor.serve_one_client(mensaje, VECES, PERIODO)
    finally:
        servidor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except struct.error as exc:
        print(f"Dato fuera de rango para su tipo: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error de red: {exc}", file=sys.stderr)
        sys.exit(1)
