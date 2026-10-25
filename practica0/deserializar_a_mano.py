"""Práctica 0: decodifica una trama a mano, sin struct, y compara con struct.

Pega en TRAMA (línea 10) la trama que imprimió tu servidor y lánzalo con
la configuración «3 · Deserializar a mano».
"""
import struct

# ------------------------------------------------------------------ configuración
# Trama del servidor (edad 22, DNI 12345678, altura 1,75 m). Cámbiala por la tuya.
TRAMA = bytes.fromhex("00 00 00 0e 01 16 00 bc 61 4e 3f e0 00 00")


def entero_sin_signo(datos: bytes) -> int:
    """Big-endian: el primer byte es el de más peso. Cada byte vale 256 veces el siguiente."""
    valor = 0
    for byte in datos:
        valor = valor * 256 + byte  # equivale a (valor << 8) | byte
    return valor


def entero_con_signo(datos: bytes) -> int:
    """Complemento a dos: si el bit más alto vale 1, el número es negativo."""
    valor = entero_sin_signo(datos)
    bits = 8 * len(datos)
    if valor >= 2 ** (bits - 1):  # bit de signo a 1
        valor -= 2 ** bits
    return valor


def real_32_bits(datos: bytes) -> float:
    """IEEE 754 de 32 bits: 1 bit de signo, 8 de exponente y 23 de mantisa."""
    bits = entero_sin_signo(datos)
    signo = bits >> 31  # bit 31
    exponente = (bits >> 23) & 0xFF  # bits 30 a 23
    mantisa = bits & 0x7FFFFF  # bits 22 a 0
    if exponente == 0:  # números muy pequeños (desnormalizados) y el cero
        valor = (mantisa / 2 ** 23) * 2 ** (-126)
    elif exponente == 0xFF:  # infinito o «no es un número» (NaN)
        valor = float("inf") if mantisa == 0 else float("nan")
    else:  # caso normal: 1,mantisa × 2^(exponente − 127)
        valor = (1 + mantisa / 2 ** 23) * 2 ** (exponente - 127)
    return -valor if signo else valor


def decodificar_a_mano(trama: bytes):
    message_size = entero_con_signo(trama[0:4])  # int32
    message_type = entero_sin_signo(trama[4:5])  # uint8
    edad = trama[5]  # uint8: un byte ya es un número de 0 a 255
    dni = entero_sin_signo(trama[6:10])  # uint32
    altura = real_32_bits(trama[10:14])  # float32
    return message_size, message_type, edad, dni, altura


def decodificar_con_struct(trama: bytes):
    message_size, message_type = struct.unpack_from(">iB", trama, 0)
    edad, dni, altura = struct.unpack_from(">BIf", trama, 5)
    return message_size, message_type, edad, dni, altura


def main() -> None:
    print(f"Trama ({len(TRAMA)} B): {TRAMA.hex(' ')}\n")
    a_mano = decodificar_a_mano(TRAMA)
    con_struct = decodificar_con_struct(TRAMA)
    nombres = ["messageSize", "messageType", "edad", "DNI", "altura"]
    for nombre, mano, st in zip(nombres, a_mano, con_struct):
        marca = "✓" if mano == st else "✗"
        print(f"{nombre:<12} a mano = {mano!s:<12} struct = {st!s:<12} {marca}")


if __name__ == "__main__":
    main()
