"""Ejemplo 1: servidor que envía la hora (8 bytes, ">d") cada PERIODO segundos."""
import socket
import struct
import sys
import time

HOST = "127.0.0.1"  # "0.0.0.0" para aceptar conexiones de otros PC
PORT = 50000
PERIODO = 0.5  # segundos entre mensajes


def atender(conexion):
    """Envía la hora al cliente cada PERIODO segundos hasta que se desconecte."""
    enviados = 0
    siguiente = time.monotonic()
    while True:
        conexion.sendall(struct.pack(">d", time.time()))
        enviados += 1
        if enviados % 10 == 0:
            print(f"{enviados} mensajes enviados")
        siguiente += PERIODO  # CAMBIA: sustituye a time.sleep(PERIODO)
        time.sleep(max(0, siguiente - time.monotonic())) # NUEVA: duerme solo lo que falta


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
        if sys.platform != "win32":
            escucha.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        escucha.bind((HOST, PORT))
        escucha.listen(1)
        while True: #linea de 29-37 cuando un cliente se va este servidor no se cierra, vuelve a esperar al sigueinte. Asi no hay que reenlazarlo otra vez.
            print(f"Esperando un cliente en {HOST}:{PORT} ...")
            conexion, direccion = escucha.accept()
            print(f"Cliente conectado desde {direccion[0]}:{direccion[1]}")
            with conexion:
                try:
                    atender(conexion)
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    print("El cliente se ha desconectado")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
