"""Ejemplo 2b: la comunicación en un hilo aparte, dentro de la clase ReceptorHora."""
import datetime
import socket
import struct
import threading
import time
from typing import NamedTuple, Optional

HOST = "127.0.0.1"
PORT = 50000


class Lectura(NamedTuple):
    """Copia del estado del receptor en un instante dado."""
    hora: Optional[float]        # hora del servidor en el último mensaje
    recibidos: int               # mensajes recibidos en total
    motivo_fin: Optional[str]    # por qué terminó el receptor (None si funciona)


class ReceptorHora:
    """Recibe en segundo plano la hora que envía el servidor y guarda la última."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._sock = None
        self._hilo = None
        # Estado compartido entre los dos hilos: solo se toca con el candado cogido.
        self._candado = threading.Lock()
        self._hora = None
        self._recibidos = 0
        self._motivo_fin = None

    def start(self):
        """Abre la conexión y lanza el hilo receptor (lo llama el hilo principal)."""
        self._sock = socket.create_connection((self.host, self.port))
        self._hilo = threading.Thread(target=self._recibir, name="receptor", daemon=True)
        self._hilo.start()
        return self

    def leer(self):
        """Devuelve una copia del último estado (lo llama el hilo principal)."""
        with self._candado:
            return Lectura(self._hora, self._recibidos, self._motivo_fin)

    def close(self):
        if self._sock is not None:
            self._sock.close()

    def _recibir(self):
        """Cuerpo del hilo receptor: lee sin parar y guarda el último dato."""
        try:
            while True:
                (hora,) = struct.unpack(">d", self._recv_exactly(8))
                with self._candado:
                    self._hora = hora
                    self._recibidos += 1
        except (ConnectionError, OSError) as exc:
            with self._candado:
                self._motivo_fin = str(exc)

    def _recv_exactly(self, size):
        datos = bytearray()
        while len(datos) < size:
            trozo = self._sock.recv(size - len(datos))
            if not trozo:
                raise ConnectionError("El servidor cerró la conexión")
            datos.extend(trozo)
        return bytes(datos)


def hora_legible(t):
    return datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def main():
    receptor = ReceptorHora(HOST, PORT).start()
    print(f"Conectado a {HOST}:{PORT}")
    try:
        while True:
            orden = input("Pulsa Enter para ver la hora del servidor (q para salir): ")
            if orden.strip().lower() == "q":
                return
            lectura = receptor.leer()
            if lectura.motivo_fin is not None:
                print(f"   Comunicación perdida: {lectura.motivo_fin}")
            elif lectura.hora is None:
                print("   Todavía no ha llegado ningún mensaje")
            else:
                print(f"   Hora del servidor: {hora_legible(lectura.hora)}"
                      f"   (edad {time.time() - lectura.hora:6.2f} s,"
                      f" {lectura.recibidos} mensajes recibidos)")
    finally:
        receptor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
