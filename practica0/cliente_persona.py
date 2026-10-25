"""Práctica 0: cliente TCP que recibe y decodifica la trama del servidor.

Tiene la misma estructura que ``ur_read_cartesian_pose.py``: conexión,
lectura exacta de bytes con ``_recv_exactly``, cabecera de 5 bytes y
decodificación del contenido con ``struct``. Solo cambia qué se lee.

Formato de la trama (big-endian):
    cabecera  ">iB"   messageSize (int32, incluye la cabecera) + messageType (uint8)
    contenido ">BIf"  edad (uint8) + DNI (uint32) + altura en metros (float32)

Se lanza desde VS Code (F5), con el servidor ya en marcha.
"""
import socket
import struct
import sys
from typing import NamedTuple, Optional

# ------------------------------------------------------------------ configuración
HOST = "127.0.0.1"  # IP del servidor: la de otro PC del laboratorio en la ampliación
PORT = 50000
# --------------------------------------------------------------------------------


class Persona(NamedTuple):
    """Datos contenidos en una trama de tipo 1."""

    edad: int
    dni: int
    altura: float


class PersonaClient:
    """Cliente TCP para el servidor de la práctica 0."""

    MESSAGE_TYPE_PERSONA = 1
    PERSONA_FORMAT = ">BIf"
    PERSONA_SIZE = struct.calcsize(PERSONA_FORMAT)

    def __init__(self, host: str = "127.0.0.1", port: int = 50000) -> None:
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None

    def connect(self) -> "PersonaClient":
        """Abre la conexión TCP con el servidor."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except OSError:
            self.sock.close()
            self.sock = None
            raise
        return self

    def close(self) -> None:
        """Cierra la conexión si estaba abierta."""
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def _recv_exactly(self, size: int) -> bytes:
        """Recibe exactamente ``size`` bytes: ``recv`` puede devolver menos."""
        if self.sock is None:
            raise ConnectionError("El cliente no está conectado")

        chunks = bytearray()
        while len(chunks) < size:
            chunk = self.sock.recv(size - len(chunks))
            if not chunk:
                raise ConnectionError("El servidor cerró la conexión")
            chunks.extend(chunk)
        return bytes(chunks)

    def read_persona(self) -> Persona:
        """Lee tramas hasta encontrar una de tipo 1 y la decodifica."""
        message_type = None
        while message_type != self.MESSAGE_TYPE_PERSONA:
            header = self._recv_exactly(5)
            message_size, message_type = struct.unpack(">iB", header)
            datos = self._recv_exactly(message_size - 5)

        if len(datos) < self.PERSONA_SIZE:
            raise struct.error("Trama de datos personales demasiado corta")
        edad, dni, altura = struct.unpack_from(self.PERSONA_FORMAT, datos) # 
        return Persona(edad, dni, altura)


def main() -> None:
    cliente = PersonaClient(host=HOST, port=PORT)
    try:
        cliente.connect()
        while True:
            persona = cliente.read_persona()
            print(f"Edad = {persona.edad} años · DNI = {persona.dni:08d} · "
                  f"Altura = {persona.altura:.2f} m")
    finally:
        cliente.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except ConnectionRefusedError:
        print("Conexión rechazada: ¿está el servidor en marcha?", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as exc:
        print(f"Fin: {exc}")
    except (OSError, struct.error) as exc:
        print(f"Error de conexión o protocolo: {exc}", file=sys.stderr)
        sys.exit(1)
