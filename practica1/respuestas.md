# Práctica 1 · Recibir datos mientras el programa trabaja: resultados

> Las medidas de referencia se tomaron en una ejecución de prueba en un solo PC. Los valores marcados con ✏️ hay que
> sustituirlos por los de mi PC.

**Dos medidas que se usan en toda la práctica**

- **Edad del dato** = hora del receptor − hora que viene en el mensaje: cuánto hace que se envió el dato que se usa.
- **Intervalo** = hora de un mensaje − hora del anterior: cada cuánto envía de verdad el emisor.

---

## Ejemplo 1 · Servidor que solo envía la hora

### Paso 2 · Referencia

```
n =    2   hora del servidor 18:03:54.915   edad      0.2 ms   intervalo   500.4 ms
n =    3   hora del servidor 18:03:55.415   edad      0.2 ms   intervalo   500.3 ms
```

✏️ Mis valores: edad ≈ `___` ms, intervalo ≈ `_____` ms.
En el mismo PC un mensaje tarda **décimas de milisegundo**. Es la referencia para todo lo demás.

### Paso 3 · Mirar dentro

Con el programa parado en la línea 36, `time.time() - t_servidor` crece cada vez que se evalúa. `t_servidor` está
fijo (es la hora del mensaje ya leído) y `time.time()` sigue avanzando: **el dato envejece mientras el programa no lo usa.**

### Experimento 1 · Un cliente lento (`PROCESADO = 2.0`)

```
n =    2   edad   1500.8 ms   intervalo   500.3 ms
n =    3   edad   3000.9 ms   intervalo   500.3 ms
n =    4   edad   4501.0 ms   intervalo   500.3 ms
```

**1. ¿Por qué la edad crece exactamente 1,5 s en cada línea?**
El cliente lee un mensaje cada 2 s, pero los mensajes consecutivos se enviaron con 0,5 s de diferencia. Cada vez que
lee, el reloj del cliente ha avanzado 2 s y la hora del mensaje solo 0,5 s: 2 − 0,5 = **1,5 s más vieja por línea**.

**2. ¿Qué valor máximo de `PROCESADO` evita que la edad crezca?**
El cliente tiene que leer al menos tan rápido como envía el servidor: `PROCESADO` + tiempo de lectura e impresión ≤ 0,5 s.
En la práctica, `PROCESADO` algo **menor que 0,5 s** (por ejemplo, 0,49). Con 0,5 exacto la edad crece muy despacio,
porque el bucle tarda un poco más que el `sleep`.
✏️ Comprobado con `PROCESADO = ____`: la edad se mantiene en ≈ `___` ms.

**3. Si mostrara la posición de un robot, ¿qué vería el operario a los 10 minutos?**
En t segundos el cliente ha leído t/2 mensajes, que el servidor envió en t/4 segundos, así que la edad es
t − t/4 = 0,75·t. A los 600 s, el operario vería **la posición de hace 7,5 minutos**, como si fuera la actual, y el
retraso seguiría creciendo. (Si el búfer de recepción llegara a llenarse, TCP frenaría al servidor con el control de
flujo, pero con 16 B/s eso tardaría horas.)

### Experimento 2 · ¿Qué devuelve realmente `recv`?

```
PROCESADO = 0.0:  recv devolvió    8 bytes = 1 mensajes y 0 bytes sueltos
PROCESADO = 2.0:  recv devolvió   32 bytes = 4 mensajes y 0 bytes sueltos
                     mensaje 1: edad   1999.5 ms
                     mensaje 2: edad   1499.2 ms
                     mensaje 3: edad    971.4 ms
                     mensaje 4: edad    470.7 ms
```

Con el cliente rápido parece que TCP entrega mensajes de 8 bytes. Con el lento, una sola llamada trae todo lo
acumulado. **TCP entrega un flujo de bytes, no mensajes**: dónde empieza y acaba cada mensaje lo decide el programa
(por eso existe `recv_exactly`).

**4. ¿Por qué este cliente lento no se queda atrás como el del experimento 1?**
Porque en cada vuelta vacía el búfer: `recv(1024)` se lleva todos los mensajes acumulados (4 en 2 s) y los procesa
todos de golpe. El último que lee siempre tiene como mucho ≈ 0,5 s. El del experimento 1 solo saca 8 bytes por vuelta
y va dejando cola.

**5. Si `recv` devuelve 20 bytes, ¿qué pasa con los 4 sobrantes y con el mensaje siguiente?**
`divmod(20, 8)` = 2 mensajes completos y 4 bytes sueltos. El bucle de las líneas 22–24 solo decodifica los 2
completos: **los 4 bytes sobrantes se descartan**. Esos 4 bytes eran la primera mitad de un mensaje, así que la
siguiente llamada a `recv` empieza a mitad de mensaje y **todos los mensajes siguientes quedan desalineados**: se
juntan la segunda mitad de uno y la primera del siguiente, y salen horas absurdas. Habría que guardar los bytes
sobrantes y anteponerlos a lo que llegue después.

### Experimento 3 · Una pausa de 10 s

✏️ Al quitar el punto de interrupción y continuar salen casi a la vez ≈ `__` mensajes (unos 20: 10 s / 0,5 s), con
edades decrecientes: ≈ 10 s, 9,5 s, 9 s… hasta ≈ 0 ms. A partir de ahí todo vuelve a la normalidad.
Es lo mismo que en el experimento 1: los mensajes esperaban en el búfer del SO. La diferencia es que aquí el cliente
sí es más rápido que el servidor, así que **se pone al día** vaciando la cola. En el experimento 1 nunca lo consigue.

### Experimento 4 · ¿Cada cuánto envía de verdad el servidor?

**6. Además de `PERIODO`, ¿qué tiempo cuenta en cada vuelta?**
El tiempo de ejecutar el resto del bucle: `time.time()`, `struct.pack`, `sendall`, el contador y el `print`, más el
**retraso del propio `sleep`** (el SO despierta al proceso un poco después de lo pedido). Por eso el intervalo
real es ≈ 500,3–500,4 ms y no 500,0.

**7. ¿Cuánto se habrá retrasado el servidor al cabo de una hora?**
✏️ Con mi medida (≈ `____` ms de más por mensaje): 7 200 mensajes × 0,35 ms ≈ **2,5 s de retraso por hora**.
El error se acumula porque cada vuelta duerme un periodo fijo a partir de donde acabó la anterior.

**Paso 7 · Corrección con `time.monotonic()`:** el servidor calcula a qué hora toca el siguiente envío
(`siguiente += PERIODO`) y duerme solo lo que falta. Los retrasos de cada vuelta ya no se suman.
✏️ Intervalo después de la corrección: ≈ `_____` ms (debería quedar en 500,0 ± unas décimas, sin deriva).

### Experimento 5 · Servidor detenido frente a servidor colgado

- **Servidor detenido (Ctrl + C):** el cliente termina con `Fin: El servidor cerró la conexión`. Al cerrarse, el SO
  del servidor envía un FIN y `recv` devuelve 0 bytes.

**8. ¿Qué muestra el cliente mientras el servidor está colgado?**
**Nada.** Ni error, ni aviso, ni fin. Se queda bloqueado en `recv` esperando bytes que no llegan. La conexión TCP
sigue abierta, porque el servidor no la ha cerrado.

**9. ¿Hay diferencia entre un servidor colgado y uno que tarda mucho en enviar?**
**No.** Desde el cliente las dos situaciones son idénticas: no llegan bytes. Con lo visto hasta aquí el cliente no
puede saber que el otro lado se ha colgado (se resuelve en el ejemplo 3 con un watchdog).

---

## Ejemplo 2 · Una tarea bloqueante y la comunicación aparte

### Versión sin hilo (paso 10)

```
Hora del servidor: 18:04:14.961   (edad   2.53 s)    ← primer Enter tras ~3 s
Hora del servidor: 18:04:15.462   (edad   4.03 s)    ← Enter tras 2 s más
Hora del servidor: 18:04:15.962   (edad   3.53 s)    ← Enter seguido
```

✏️ Mis edades: `____` s, `____` s, `____` s…

**10. Mientras el programa espera en `input()`, ¿quién lee el socket? ¿Dónde están los mensajes?**
**Nadie** lee el socket: el único hilo del programa está bloqueado en `input()`. Los mensajes se acumulan en el
**búfer de recepción del sistema operativo**.

**11. Al pulsar Enter, ¿se lee el más reciente o el más antiguo?**
**El más antiguo** de la cola. TCP entrega los bytes en orden (FIFO).

**12. ¿Qué edad tendrá el dato si el operario tarda 1 minuto? ¿Y si luego pulsa Enter 10 veces seguidas?**
Tras un minuto, la edad será de **≈ 60 s**: se lee el primer mensaje que llegó durante la espera. Cada Enter rápido
saca el siguiente de la cola, que es 0,5 s más reciente, mientras el reloj apenas avanza. La edad baja unos 0,5 s
por pulsación: tras 10 pulsaciones, **≈ 55 s**. Para ponerse al día habría que pulsar unas 120 veces.

### Versión con hilo (paso 11)

```
Hora del servidor: 18:04:22.466   (edad   0.04 s, 6 mensajes recibidos)
Hora del servidor: 18:04:24.467   (edad   0.04 s, 10 mensajes recibidos)
```

La edad ya no depende de lo que tarde el operario, y el contador demuestra que el receptor seguía trabajando mientras
el principal esperaba.

**Paso 12:** en *Pila de llamadas* aparecen dos hilos: `MainThread` (parado en `input()`) y `receptor`
(en la línea 56).

**Paso 13:** con el servidor detenido → `Comunicación perdida: El servidor cerró la conexión`.

**13. ¿Por qué con el hilo la edad nunca supera 0,5 s? ¿Qué mensajes se pierden? ¿Importa?**
El receptor lee cada mensaje en cuanto llega y **sobrescribe** `_hora` con el último. Cuando el principal pregunta, el
dato tiene como mucho un periodo (0,5 s) de antigüedad. Se «pierden» (se sobrescriben sin usarse) todos los
intermedios entre dos consultas del operario. **No importa**, porque el programa solo quiere la hora actual, no el
histórico. (Si importara, por ejemplo para registrar una trayectoria, habría que usar una cola en vez de una sola variable.)

**14. Sustituyendo `input(...)` por `time.sleep(3)`, ¿cambia algo?**
El comportamiento es el mismo, porque `sleep` también bloquea el hilo.
- **Sin hilo:** lee un mensaje cada 3 s mientras llegan 6, y la edad crece 2,5 s por vuelta, como el cliente lento.
- **Con hilo:** la edad se mantiene ≤ 0,5 s, porque el receptor no se ve afectado.

**15. ¿Qué pasaría si `_recibir` hiciera el `recv` dentro del `with self._candado:`?**
El receptor tendría el candado cogido casi todo el tiempo, porque pasa casi todo el tiempo bloqueado en `recv`.
`leer()` tendría que esperar a que llegara un mensaje para poder entrar: **el hilo principal volvería a quedar
bloqueado por la red**, hasta 0,5 s en cada consulta y **para siempre** si el servidor se cuelga. Por eso, dentro de
una sección crítica nunca se espera a nada: solo se copian o asignan valores.

**16. Con el servidor colgado, ¿qué dice el programa? ¿Qué le falta al operario?**
Sigue mostrando la **última hora recibida**, con una edad que crece y el contador congelado. No da ningún error ni
aviso. Al operario le falta una **alarma explícita** de que no llegan datos, por ejemplo «sin datos desde hace X s».
Ahora tendría que deducirlo él mirando la edad.

**17. ¿Qué ventaja tiene que el estado compartido viva en un objeto y solo se lea con `leer()`?**
- **Encapsulación:** desde fuera nadie puede tocar el estado sin el candado, y el principal no sabe nada de
  sockets ni hilos.
- **`leer()` devuelve una copia coherente** (hora, recibidos y motivo_fin del mismo instante).
- **Se pueden crear varias instancias.** Para recibir de dos servidores basta con
  `ReceptorHora(ip1, ...)` y `ReceptorHora(ip2, ...)`: cada uno con su socket, su hilo, su candado y su estado,
  sin variables globales que se pisen.

---

## Ejemplo 3 · Supervisor con watchdog

Salida de referencia con 3 dispositivos: uno sano, uno que se va (Ctrl + C) y uno colgado:

```
--- 18:04:31 · 3 dispositivos · 5 hilos ---
  127.0.0.1:40036       OK            silencio   0.5 s   recibidos     5
  127.0.0.1:40038       OK            silencio   0.5 s   recibidos     5
  127.0.0.1:40052       OK            silencio   0.5 s   recibidos     5
--- 18:04:33 · 3 dispositivos · 4 hilos ---
  127.0.0.1:40036       OK            silencio   0.5 s   recibidos     9
  127.0.0.1:40038       DESCONECTADO  silencio   2.0 s   recibidos     6
  127.0.0.1:40052       SIN DATOS     silencio   2.0 s   recibidos     6
--- 18:04:37 · 3 dispositivos · 4 hilos ---
  127.0.0.1:40052       EXPULSADO     silencio   6.0 s   recibidos     6
--- 18:04:38 · 3 dispositivos · 3 hilos ---
```

✏️ Paso 16: al continuar el dispositivo expulsado muestra `El supervisor ha cerrado la conexión` (o el error de
conexión que aparezca: `_______________`).

**18. ¿Cómo cambia el número de hilos en los pasos 14 y 15? ¿Qué hilos son?**
- Base: **2** hilos, el principal (`MainThread`, que hace de watchdog) y el `aceptador`.
- Por cada dispositivo, **+1** hilo `disp-<puerto>`. Con 4 dispositivos son 6.
- Paso 15: el que se va con Ctrl + C cierra la conexión, su `recv` devuelve 0 y su hilo termina (**−1**). El colgado
  mantiene su hilo bloqueado en `recv` hasta que el watchdog lo expulsa con `shutdown`, y entonces termina (**−1**).

**19. ¿Por qué un hilo por dispositivo? ¿Qué pasaría con uno solo que hiciera `recv` por turnos?**
Porque `recv` bloquea. Con un solo hilo por turnos, al llegar al dispositivo colgado se quedaría bloqueado en su
`recv` para siempre y **dejaría de atender a todos los demás**: un solo equipo colgado tumbaría el sistema entero.

**20. ¿Qué pasaría con `WATCHDOG = 0.4`? ¿Y con `30`? ¿De qué depende el valor adecuado?**
- **0,4 s** es menor que el periodo (0,5 s): dispositivos sanos pasarían a SIN DATOS a menudo (**falsas alarmas**).
- **30 s** detectaría un fallo muy tarde. Además, con `EXPULSAR_TRAS = 5` el dispositivo se expulsaría antes de
  marcarse como SIN DATOS, así que ese estado no se vería nunca.
- **Depende de:** el periodo de envío del dispositivo, la variabilidad (*jitter*) de la red y del SO, y cuánto
  tiempo puede permitirse el proceso sin datos antes de que sea peligroso. Lo habitual es unos 2–3 periodos (aquí,
  1,5 s = 3 periodos).

**21. ¿Por qué el dispositivo relanzado aparece como nuevo? ¿Qué añadirías al protocolo?**
Porque el supervisor identifica a cada dispositivo por `IP:puerto`, y el puerto es **efímero**: el SO asigna uno
distinto en cada conexión. Habría que añadir un **identificador propio del dispositivo** (número de serie o nombre),
por ejemplo en un mensaje de presentación al conectarse o en una cabecera de cada mensaje, y usarlo como clave del
diccionario.

**22. Con 1 000 dispositivos, ¿cuántos hilos? ¿Es razonable?**
**1 002** (1 000 + principal + aceptador). **No es razonable**: cada hilo reserva memoria para su pila, y el SO
pierde tiempo conmutando entre ellos. Para muchas conexiones se usa **E/S multiplexada**: un solo hilo que vigila
todos los sockets con `select` o `selectors`, o `asyncio`.

**23. ¿Qué habría que añadir al cliente del experimento 5 para que avisara de que el servidor dejó de enviar?**
Un **watchdog**. Hay dos formas:
- Poner un **timeout** al socket, por ejemplo `sock.settimeout(1.5)`, y capturar `socket.timeout` para avisar.
- Recibir en un hilo, guardando `time.monotonic()` de la última recepción, y que el principal compruebe cada cierto
  tiempo si el silencio supera el umbral.

---

## Experimentos rápidos

| # | Qué se hizo | Qué se ve | Causa |
|---|---|---|---|
| 1 | Cliente sin servidor | `Conexión rechazada: ¿está el servidor en marcha?` | Nadie escucha en el puerto: el SO responde con RST |
| 2 | Servidor dos veces | `[WinError 10048]` / `Address already in use` | El puerto 50000 ya está en uso |
| 3 | Servidor con `PERIODO = 0.05` y cliente con `PROCESADO = 2.0` | La edad crece ≈ **1,95 s por línea** | 2 − 0,05 = 1,95 s. Además, el búfer se llena 10 veces más rápido |
| 4 | Servidor con `">f"` | El cliente termina con un error al convertir la hora (`OverflowError: timestamp out of range`) | Cada mensaje mide ahora 4 bytes: el cliente junta dos en 8 bytes y los lee como un `double`, lo que da un número absurdo. Además, `">f"` no puede guardar la hora: 1791306000.25 → 1791305984.0 (16 s de error) |
| 5 | Cliente con `"<d"` | El mismo tipo de error | Los 8 bytes son correctos, pero se leen en el orden equivocado |
| 6 | Supervisor con `WATCHDOG = 0.4` | Dispositivos sanos pasan a SIN DATOS de vez en cuando | El umbral es menor que el periodo de envío (0,5 s) |
| 7 | Dispositivo con `PERIODO = 2.0` | Alterna entre OK y SIN DATOS aunque funciona | 2 s de silencio entre mensajes > 1,5 s de umbral. El watchdog debe ajustarse al periodo de cada equipo |

---

## Ampliación · Dos PC (si se hace en el laboratorio)

✏️ Paso 17, edad del dato entre dos PC: `______` ms (puede ser de milisegundos, de segundos o incluso negativa).

**24. ¿Cómo distinguir la parte de la edad debida a la red de la debida a los relojes?**
- La diferencia entre relojes es casi **constante**. El retardo de red es pequeño y **variable**.
- Se puede medir la red con un solo reloj: el `ping` da el tiempo de ida y vuelta (RTT), y RTT/2 ≈ retardo de ida.
  También se puede hacer que el cliente devuelva cada mensaje y el servidor mida la ida y vuelta con su propio reloj.
- Lo que sobra de la edad respecto a RTT/2 es, aproximadamente, la **diferencia entre los relojes**.

**25. ¿Qué haría falta para que la edad fuera fiable entre dos equipos?**
**Sincronizar los relojes** de los dos equipos. En oficina se usa **NTP** (precisión de milisegundos). En
industria, cuando hace falta precisión de microsegundos, se usa **PTP (IEEE 1588)**.

**26. En el paso 18, ¿en qué estado aparece el dispositivo desconectado? ¿Por qué no como DESCONECTADO?**
✏️ Aparece como **SIN DATOS** y, a los 5 s, **EXPULSADO**. Al quitar el cable el dispositivo no puede enviar el FIN
de cierre de TCP, y el supervisor no le envía nada que pudiera fallar, así que **TCP no se entera** de que la
conexión está rota: `recv` sigue esperando. DESCONECTADO solo aparece cuando el otro extremo cierra de forma
ordenada. Un cable cortado solo lo detecta el **watchdog**.
