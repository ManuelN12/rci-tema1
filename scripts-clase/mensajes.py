"""Mensajes compartidos por cliente.py y servidor.py (trabajo de clase).

Trama de 13 bytes, big-endian (">BId"):
    edad   uint8   (1 B)
    dni    uint32  (4 B)
    altura float64 (8 B)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass
class Dato:
    edad: int
    dni: int
    altura: float

    FORMATO = ">BId"  # atributo de clase: no forma parte de los campos del dataclass

    def codificar(self) -> bytes:
        return struct.pack(self.FORMATO, self.edad, self.dni, self.altura)

    @classmethod
    def decodificar(cls, trama: bytes) -> Dato:
        edad, dni, altura = struct.unpack(cls.FORMATO, trama)
        return cls(edad=edad, dni=dni, altura=altura)

    @classmethod
    def tamano(cls) -> int:
        return struct.calcsize(cls.FORMATO)
