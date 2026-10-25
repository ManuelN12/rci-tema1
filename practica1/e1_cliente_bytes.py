"""Ejemplo 1: muestra cuántos bytes devuelve cada llamada a recv(1024)."""
import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 50000
PROCESADO = 0.0


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        print(f"Conectado a {HOST}:{PORT}")
        while True:
            datos = sock.recv(1024)
            if not datos:
                print("Fin: el servidor cerró la conexión")
                return
            completos, sobran = divmod(len(datos), 8)
            print(f"recv devolvió {len(datos):4d} bytes = {completos} mensajes"
                  f" y {sobran} bytes sueltos")
            for i in range(completos):
                (t,) = struct.unpack_from(">d", datos, 8 * i)
                print(f"   mensaje {i + 1}: edad {(time.time() - t) * 1000:8.1f} ms")
            time.sleep(PROCESADO)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
