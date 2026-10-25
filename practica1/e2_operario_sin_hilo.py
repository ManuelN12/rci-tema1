"""Ejemplo 2a: la tarea bloqueante (input) y la comunicación en el mismo hilo."""
import datetime
import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 50000


def recv_exactly(sock, size):
    datos = bytearray()
    while len(datos) < size:
        trozo = sock.recv(size - len(datos))
        if not trozo:
            raise ConnectionError("El servidor cerró la conexión")
        datos.extend(trozo)
    return bytes(datos)


def hora_legible(t):
    return datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Conectado a {HOST}:{PORT}")
        while True:
            orden = input("Pulsa Enter para ver la hora del servidor (q para salir): ")
            if orden.strip().lower() == "q":
                return
            (t_servidor,) = struct.unpack(">d", recv_exactly(sock, 8))
            print(f"   Hora del servidor: {hora_legible(t_servidor)}"
                  f"   (edad {time.time() - t_servidor:6.2f} s)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except ConnectionError as exc:
        print(f"Fin: {exc}")
