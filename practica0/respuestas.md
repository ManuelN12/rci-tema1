# Práctica 0 · Cliente y servidor TCP en el mismo PC: resultados

> Resultados obtenidos en mi PC (Windows, Python 3.15.1, VS Code).
## Montaje

- Servidor en `127.0.0.1:50000` (loopback). El cliente usa un puerto efímero que elige el sistema operativo.
  Puertos efímeros del cliente en mis ejecuciones: `65197` y, en otra, `50154`: cambia en cada conexión.
- Trama de 14 bytes en big-endian: cabecera `">iB"` (messageSize = 14, messageType = 1) + contenido `">BIf"`.

Para edad 22, DNI 12345678 y altura 1,75 m:

```
00 00 00 0e | 01 | 16 | 00 bc 61 4e | 3f e0 00 00
messageSize  type  edad      DNI         altura
    14         1    22    12345678       1.75
```

## Elección de tipos

| Campo | Tipo | Por qué |
|---|---|---|
| edad | `B` uint8 | 0–255 cubre cualquier edad. Usar más bytes sería desperdiciarlos |
| DNI | `I` uint32 | 8 cifras (hasta 99 999 999) no caben en 16 bits (máx. 65 535). En 32 bits caben hasta 4 294 967 295 |
| altura | `f` float32 | Unas 7 cifras significativas bastan para metros con centímetros. Con `d` serían 8 bytes en vez de 4 |

## Paso 6 · Los bytes en el depurador

```
datos.hex(" ")  ->  '16 00 bc 61 4e 3f e0 00 00'
list(datos)     ->  [22, 0, 188, 97, 78, 63, 224, 0, 0]
```

El panel Variables muestra `b'\x16\x00\xbcaN?\xe0\x00\x00'`. Python escribe como carácter cada byte que es ASCII
imprimible (`0x61` = `a`, `0x4e` = `N`, `0x3f` = `?`). Son los mismos 9 bytes, solo cambia cómo se muestran.

**Idea clave:** mientras el cliente está parado en un punto de interrupción, el servidor sigue enviando. Las tramas no se
pierden: se quedan en el **búfer de recepción del sistema operativo** del cliente y se leen en orden al continuar.

## Paso 8 · Deserializar a mano

```
messageSize  a mano = 14           struct = 14           ✓
messageType  a mano = 1            struct = 1            ✓
edad         a mano = 22           struct = 22           ✓
DNI          a mano = 12345678     struct = 12345678     ✓
altura       a mano = 1.75         struct = 1.75         ✓
```

- **DNI** `00 bc 61 4e` = 0·256³ + 188·256² + 97·256 + 78 = **12 345 678**
- **Altura** `3f e0 00 00` = `0 | 01111111 | 1100000…0`
  - signo = 0 → positivo
  - exponente = 127 → 2^(127−127) = 2⁰ = 1
  - mantisa = 0x600000 / 2²³ = 0,75
  - valor = (1 + 0,75) × 1 = **1,75**

Con el punto de interrupción en la línea 36 obtuve: signo = `0`, exponente = `127`, mantisa = `6291456`
(6 291 456 / 2²³ = 0,75 → (1 + 0,75) × 2⁰ = 1,75).

- Si la altura fuera **−1,75**, solo cambiaría el **signo** (0 → 1): `bf e0 00 00`.
- Si fuera **3,5** (= 1,75 × 2), solo cambiaría el **exponente** (127 → 128): `40 60 00 00`.

## Experimentos rápidos

| # | Qué se hizo | Qué se ve | Capa | Explicación |
|---|---|---|---|---|
| 1 | Lanzar el cliente sin el servidor | `Conexión rechazada: ¿está el servidor en marcha?` | 4 · Transporte | Nadie escucha en el puerto 50000. El SO del servidor responde al SYN con un RST |
| 2 | Lanzar el servidor dos veces | `OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted` | 4 · Transporte | Un puerto solo puede tenerlo un socket en escucha a la vez |
| 3 | `EDAD = 300` | `Dato fuera de rango para su tipo: 'B' format requires 0 <= number <= 255` | 7 · Aplicación | 300 no cabe en un byte sin signo. `struct.pack` comprueba el rango antes de enviar |
| 4 | `DNI = 5000000000` | `'I' format requires 0 <= number <= 4294967295` | 7 · Aplicación | 5·10⁹ supera el máximo de 32 bits (≈ 4,29·10⁹) |
| 5 | Cliente con `"<BIf"` | `Edad = 22 · DNI = 1315027968 · Altura = 0.00 m` | 7 · Aplicación | No hay error, pero los datos son absurdos: los bytes se leen al revés. La edad sale bien porque ocupa 1 byte y el orden no le afecta. **Es el error más peligroso, porque no avisa** |
| 6 | `netstat -an` con los dos en marcha | Una línea `LISTENING` en `127.0.0.1:50000` y dos `ESTABLISHED`, una por cada extremo (ver abajo) | 4 · Transporte | Hay 3 sockets: el de escucha del servidor, el de la conexión del servidor (`conexion`) y el del cliente |

Salida de `netstat -an | findstr 50000` con servidor y cliente en marcha:

```
TCP    127.0.0.1:50000        0.0.0.0:0              LISTENING     ← socket de escucha del servidor (listen)
TCP    127.0.0.1:50000        127.0.0.1:50154        ESTABLISHED   ← conexión, lado servidor (socket de accept)
TCP    127.0.0.1:50154        127.0.0.1:50000        ESTABLISHED   ← conexión, lado cliente
```

Una conexión TCP tiene dos extremos, cada uno identificado por IP:puerto, y por eso las dos últimas líneas son espejo
una de la otra. `accept()` crea un socket nuevo por cliente y el de escucha sigue aparte.

**Nota sobre el experimento 2.** Me salió sin querer: pulsé F5 con el desplegable todavía en «1 · Servidor» mientras
tenía abierto el cliente. F5 lanza la configuración elegida en el desplegable, no el archivo abierto.

Comprobación del experimento 5: con `<`, el DNI se lee de los bytes `00 bc 61 4e` como little-endian:
0x4e61bc00 = 1 315 027 968.

## Ampliación · Dos PC (si se hace en el laboratorio)

- ✏️ IP del PC servidor (`ipconfig`): `__________`
- ✏️ ¿Responde el `ping`? `___`
- Servidor con `HOST = "0.0.0.0"`: escucha en todas las interfaces. Con `127.0.0.1` solo acepta conexiones del propio PC.
- ✏️ `arp -a` en el cliente: IP del servidor → MAC `__-__-__-__-__-__`. En loopback no hacía falta ARP.
- `TimeoutError` → cortafuegos bloqueando. `ConnectionRefusedError` → servidor apagado o escuchando solo en `127.0.0.1`.
