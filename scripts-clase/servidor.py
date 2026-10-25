"""Servidor TCP didáctico: recibe un Dato y luego juega al «ping-pong» con un contador."""
import socket

from mensajes import Dato

HOST = "0.0.0.0"
PUERTO = 33334


def recv_exactly(sock, size):
    """recv puede devolver menos bytes de los pedidos: se repite hasta completar."""
    datos = bytearray()
    while len(datos) < size:
        trozo = sock.recv(size - len(datos))
        if not trozo:
            raise ConnectionError("El cliente cerró la conexión")
        datos.extend(trozo)
    return bytes(datos)


def main():
    # Crear el socket, asociarlo al puerto y empezar a escuchar.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PUERTO))
        servidor.listen(1)
        print(f"Esperando una conexión en el puerto {PUERTO}...")

        # Aceptar un cliente y esperar hasta recibir datos.
        conexion, direccion = servidor.accept()
        with conexion:
            print(f"Cliente conectado: {direccion}")
            datos = recv_exactly(conexion, Dato.tamano())
            datos_recibidos = Dato.decodificar(datos)
            print(f"Primeros datos recibidos: {datos_recibidos}")

            contador = 0
            while contador < 1000:
                print(f"Servidor enviado: {contador}")
                conexion.sendall(contador.to_bytes(4, "big"))
                contador_vuelta = int.from_bytes(recv_exactly(conexion, 4), "big")
                print(f"Servidor recibido: {contador_vuelta}")
                contador = contador_vuelta + 1


if __name__ == "__main__":
    main()
