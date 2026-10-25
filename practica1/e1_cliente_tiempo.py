"""Ejemplo 1: cliente que recibe la hora y muestra su edad y el intervalo."""
import datetime
import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 50000
PROCESADO = 0.0  # segundos que «tarda» el programa con cada dato


def recv_exactly(sock, size):
    """Recibe exactamente size bytes (igual que en la práctica 0)."""
    datos = bytearray()
    while len(datos) < size:
        trozo = sock.recv(size - len(datos))
        if not trozo:
            raise ConnectionError("El servidor cerró la conexión")
        datos.extend(trozo)
    return bytes(datos)


def hora_legible(t):
    """Convierte segundos desde 1970 en hh:mm:ss.mmm."""
    return datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Conectado a {HOST}:{PORT}")
        anterior = None
        n = 0
        while True:
            (t_servidor,) = struct.unpack(">d", recv_exactly(sock, 8))
            n += 1
            edad = time.time() - t_servidor
            texto = f"n = {n:4d}   hora del servidor {hora_legible(t_servidor)}"
            texto += f"   edad {edad * 1000:8.1f} ms"
            if anterior is not None:
                texto += f"   intervalo {(t_servidor - anterior) * 1000:7.1f} ms"
            print(texto)
            anterior = t_servidor
            time.sleep(PROCESADO)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except ConnectionRefusedError:
        print("Conexión rechazada: ¿está el servidor en marcha?")
    except ConnectionError as exc:
        print(f"Fin: {exc}")
