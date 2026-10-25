"""Cliente TCP didáctico: envía un Dato y luego juega al «ping-pong» con un contador."""
import socket

from mensajes import Dato

HOST = "127.0.0.1"
PUERTO = 33334


def main():
    datos_enviar = Dato(edad=30, dni=87666666, altura=1.56)

    with socket.create_connection((HOST, PUERTO)) as cliente:
        cliente.sendall(datos_enviar.codificar())

        while True:
            bytes_recibidos = cliente.recv(4)
            if not bytes_recibidos:
                break
            contador = int.from_bytes(bytes_recibidos, "big")
            print(f"Cliente recibido {contador}")
            contador += 1
            cliente.sendall(contador.to_bytes(4, "big"))
            print(f"Cliente enviado {contador}")


if __name__ == "__main__":
    main()
