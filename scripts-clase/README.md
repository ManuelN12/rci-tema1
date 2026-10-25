# Scripts de clase

Variante de la práctica 0 hecha en clase. El cliente envía un `Dato` (edad, DNI y altura) y después cliente y servidor
se pasan un contador de 4 bytes, sumando 1 cada uno, hasta llegar a 1000.

## Trama del `Dato` (13 bytes, `">BId"`)

| Campo | Tipo | Bytes |
|---|---|---|
| edad | `B` uint8 | 1 |
| dni | `I` uint32 | 4 |
| altura | `d` float64 | 8 |

A diferencia de la práctica 0, la altura va en `d` (64 bits) y no hay cabecera.

## Cambios respecto a la versión de clase

Los scripts originales no se podían ejecutar:

1. **Faltaba `mensajes.py`.** Los dos hacían `from mensajes import Dato`, pero ese archivo no existía, y además
   cada script redefinía la clase `Dato`. Ahora `Dato` vive solo en `mensajes.py` y los dos lo importan.
2. **`decodificar` es un `@classmethod`.** Antes había que crear un `Dato` falso (`Dato(3, 3, 1.5)`) para
   poder llamar a `decodificar`. Ahora basta con `Dato.decodificar(trama)`.
3. **El servidor usa `recv_exactly`.** `recv(1024)` puede devolver menos bytes de los que ocupa el mensaje
   (TCP entrega un flujo de bytes, no mensajes), así que el servidor pide exactamente `Dato.tamano()` = 13 bytes
   y luego 4 por cada contador.
4. Se eliminaron los `import struct` duplicados y se unificó la sangría a 4 espacios.
