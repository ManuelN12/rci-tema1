# RCI · Tema 1 · Fundamentos de redes (TCP/IP en entornos industriales)

**Asignatura:** Redes de Comunicación Industriales · Máster en Electrónica Industrial · Universidad de Deusto
**Curso:** 2026–2027
**Alumno:** Manuel Narváez

Prácticas y trabajo de clase del Tema 1. Todo se ejecuta en un solo PC por la interfaz de *loopback* (`127.0.0.1`).
Las ampliaciones entre dos PC del laboratorio se indican en cada práctica.

## Contenido

| Carpeta | Qué hay | Conceptos |
|---|---|---|
| [`practica0/`](practica0/) | Cliente y servidor TCP en el mismo PC. Trama binaria de 14 B (edad, DNI y altura) | Sockets, `struct`, big-endian, IEEE 754, deserializar a mano |
| [`practica1/`](practica1/) | Recibir datos mientras el programa trabaja | Edad del dato, flujo de bytes de TCP, hilos y candados, watchdog |
| [`scripts-clase/`](scripts-clase/) | Ejercicio hecho en clase: cliente y servidor que intercambian un `Dato` y un contador | `dataclass`, `struct`, protocolo de ida y vuelta |

Cada práctica tiene un `respuestas.md` con los resultados de los experimentos y las respuestas a las preguntas del enunciado.

## Requisitos

- Python 3.10 o posterior (solo biblioteca estándar: no hace falta instalar nada con `pip`).
- VS Code con la extensión **Python** de Microsoft (para depurar con F5).

## Cómo ejecutar

### Práctica 0

Abre la carpeta `practica0` en VS Code (**Archivo → Abrir carpeta…**). En **Ejecutar y depurar** (Ctrl + Mayús + D) hay tres configuraciones:

1. **1 · Servidor**: lánzala primero.
2. **2 · Cliente**: muestra edad, DNI y altura de cada trama.
3. **3 · Deserializar a mano**: decodifica la trama sin `struct` y compara.

Desde un terminal:

```bash
cd practica0
python servidor_persona.py      # terminal 1
python cliente_persona.py       # terminal 2
python deserializar_a_mano.py
```

### Práctica 1

```bash
cd practica1
# Ejemplos 1 y 2: servidor de hora (puerto 50000)
python e1_servidor_tiempo.py    # déjalo en marcha
python e1_cliente_tiempo.py     # o e1_cliente_bytes.py, e2_operario_sin_hilo.py, e2_operario_con_hilo.py

# Ejemplo 3: supervisor con watchdog (puerto 50001)
python e3_supervisor.py         # terminal 1
python e3_dispositivo.py        # uno por terminal, tantos como quieras
```

### Scripts de clase

```bash
cd scripts-clase
python servidor.py              # terminal 1
python cliente.py               # terminal 2
```

## Notas

- Los números de línea de los programas coinciden con los del enunciado de cada práctica.
- Los datos personales de la práctica 0 son inventados (DNI 12345678).
