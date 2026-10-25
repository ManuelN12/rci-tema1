"""Ejemplo 3: dispositivo que envía su hora al supervisor cada PERIODO segundos."""
import socket
import struct
import time

HOST = "127.0.0.1"  # IP del supervisor
PORT = 50001
PERIODO = 0.5


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        ip, puerto = sock.getsockname()
        print(f"Conectado al supervisor desde {ip}:{puerto}")
        while True:
            sock.sendall(struct.pack(">d", time.time()))
            time.sleep(PERIODO)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDispositivo detenido.")
    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
        print("El supervisor ha cerrado la conexión")
