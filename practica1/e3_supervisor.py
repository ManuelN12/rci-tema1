"""Ejemplo 3: supervisor que atiende a varios dispositivos y los vigila (watchdog)."""
import socket
import struct
import sys
import threading
import time

HOST = "127.0.0.1"   # "0.0.0.0" para aceptar dispositivos de otros PC
PORT = 50001
WATCHDOG = 1.5       # s sin datos para pasar a SIN DATOS (3 periodos)
EXPULSAR_TRAS = 5.0  # s sin datos para cerrar la conexión
OLVIDAR_TRAS = 10.0  # s que se sigue mostrando un dispositivo que ya no está
REVISION = 1.0       # s entre revisiones del watchdog


class Dispositivo:
    """Lo que el supervisor sabe de un dispositivo conectado."""

    def __init__(self, sock, direccion):
        self.sock = sock
        self.direccion = direccion
        self.conectado = True
        self.expulsado = False
        self.ultima_recepcion = time.monotonic()  # reloj local: para el watchdog
        self.retardo = None                       # hora local − hora del dispositivo
        self.recibidos = 0
        self.momento_fin = None


class Supervisor:
    """Atiende a cada dispositivo en su hilo y los vigila desde el hilo principal."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Estado compartido por todos los hilos: solo se toca con el candado cogido.
        self._candado = threading.Lock()
        self._dispositivos = {}  # dirección -> Dispositivo

    def run(self):
        """Hilo principal: abre el puerto, lanza el aceptador y revisa cada segundo."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
            if sys.platform != "win32":
                escucha.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            escucha.bind((self.host, self.port))
            escucha.listen()
            print(f"Supervisor esperando dispositivos en {self.host}:{self.port}")
            threading.Thread(target=self._aceptar, args=(escucha,),
                             name="aceptador", daemon=True).start()
            while True:
                time.sleep(REVISION)
                self._revisar()

    def _aceptar(self, escucha):
        """Hilo aceptador: espera dispositivos nuevos y lanza un hilo para cada uno."""
        while True:
            sock, (ip, puerto) = escucha.accept()
            d = Dispositivo(sock, f"{ip}:{puerto}")
            with self._candado:
                self._dispositivos[d.direccion] = d
            threading.Thread(target=self._atender, args=(d,),
                             name=f"disp-{puerto}", daemon=True).start()

    def _atender(self, d):
        """Un hilo por dispositivo: recibe hasta que la conexión se cierra."""
        try:
            while True:
                (t_dispositivo,) = struct.unpack(">d", self._recv_exactly(d.sock, 8))
                with self._candado:
                    d.ultima_recepcion = time.monotonic()
                    d.retardo = time.time() - t_dispositivo
                    d.recibidos += 1
        except (ConnectionError, OSError):
            pass
        finally:
            with self._candado:
                d.conectado = False
                d.momento_fin = time.monotonic()
            d.sock.close()

    def _revisar(self):
        """Watchdog: clasifica a cada dispositivo, expulsa a los mudos y muestra la tabla."""
        ahora = time.monotonic()
        filas = []
        with self._candado:
            for direccion, d in list(self._dispositivos.items()):
                silencio = ahora - d.ultima_recepcion
                if d.conectado and silencio > EXPULSAR_TRAS:
                    d.expulsado = True
                    try:
                        d.sock.shutdown(socket.SHUT_RDWR)  # despierta a su hilo
                    except OSError:
                        pass
                if d.expulsado:
                    estado = "EXPULSADO"
                elif not d.conectado:
                    estado = "DESCONECTADO"
                elif silencio > WATCHDOG:
                    estado = "SIN DATOS"
                else:
                    estado = "OK"
                if not d.conectado and ahora - d.momento_fin > OLVIDAR_TRAS:
                    del self._dispositivos[direccion]
                    continue
                retardo = "     —" if d.retardo is None else f"{d.retardo * 1000:6.1f}"
                filas.append(f"  {direccion:<21} {estado:<13} silencio {silencio:5.1f} s"
                             f"   recibidos {d.recibidos:5d}   retardo {retardo} ms")
        print(f"--- {time.strftime('%H:%M:%S')} · {len(filas)} dispositivos"
              f" · {threading.active_count()} hilos ---")
        for fila in filas:
            print(fila)

    @staticmethod
    def _recv_exactly(sock, size):
        datos = bytearray()
        while len(datos) < size:
            trozo = sock.recv(size - len(datos))
            if not trozo:
                raise ConnectionError("conexión cerrada")
            datos.extend(trozo)
        return bytes(datos)


if __name__ == "__main__":
    try:
        Supervisor(HOST, PORT).run()
    except KeyboardInterrupt:
        print("\nSupervisor detenido.")
