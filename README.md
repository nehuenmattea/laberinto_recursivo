# Laberinto Recursivo con Backtracking

Aplicación de escritorio en Python (Tkinter) que genera laberintos aleatorios y los resuelve visualmente mediante un algoritmo **recursivo de backtracking exhaustivo**. Permite jugar manualmente con las flechas/WASD o ver cómo el algoritmo explora todo el laberinto, vuelve al punto de partida y luego recorre la ruta más corta hacia la salida óptima.

Proyecto realizado para la materia **Algoritmos y Estructuras de Datos III** (Trabajo Práctico de Recursividad).

## Características

- **Generación procedural de laberintos** mediante el algoritmo *Recursive Backtracker*, con inercia direccional para lograr pasillos fluidos (evita el aspecto de "ruido" o patrón tipo QR).
- **Apertura controlada de ciclos**: se eliminan paredes puntuales para crear caminos alternativos, sin generar bloques 2x2 abiertos ni postes de pared aislados.
- **Dos salidas** ubicadas en cuadrantes distintos y a una distancia mínima del inicio y entre sí, para que cada partida sea distinta.
- **Modo manual**: mové el jugador con las flechas del teclado o con WASD.
- **Modo automático**: un algoritmo recursivo de backtracking explora **todo** el laberinto celda por celda, sin repetir caminos, y vuelve al inicio; luego anima el recorrido más corto hacia la salida ganadora.
- **Panel de estadísticas** con la solución óptima, comparación entre ambas salidas y métricas del árbol de recursión (llamadas, avances, retrocesos, callejones sin salida).
- Interfaz gráfica simple construida con Tkinter, sin dependencias externas.

## Vista general de la interfaz

- **Barra superior**: botones para generar un nuevo laberinto, resolver automáticamente, detener la animación y ver estadísticas.
- **Canvas central**: representación visual del laberinto (paredes, inicio, salidas y jugador).
- **Barra inferior**: mensajes de estado sobre lo que está ocurriendo.

Colores del laberinto:

| Elemento | Color |
|---|---|
| Pared | Azul pizarra oscuro |
| Celda libre | Blanco suave |
| Inicio (I) | Verde esmeralda |
| Salida 1 (S1) | Rojo carmesí |
| Salida 2 (S2) | Naranja ámbar |
| Avance (exploración) | Celeste |
| Retroceso (exploración) | Melocotón |
| Ruta óptima | Verde brillante |
| Jugador | Púrpura |

## Estructura del proyecto

```
.
├── main.py            # Punto de entrada de la aplicación
├── gui.py             # Interfaz gráfica (Tkinter) y animaciones
├── laberinto.py        # Lógica de generación del laberinto
└── test_laberinto.py   # Tests unitarios (unittest)
```

### `laberinto.py`

Define la clase `Laberinto`, responsable de:

- Generar el laberinto sobre una grilla de celdas (por defecto 21x21) usando un algoritmo recursivo tipo *Recursive Backtracker*.
- Garantizar que el resultado no tenga artefactos visuales indeseados (bloques 2x2 completamente libres o paredes aisladas).
- Elegir dos salidas (`SALIDA1` y `SALIDA2`) en callejones alejados del inicio y entre sí, ubicadas en cuadrantes distintos.
- Exponer utilidades de consulta como `valor(r, c)`, `es_transitable(r, c)` y `es_meta(r, c)`, usadas tanto por la GUI como por el algoritmo de resolución.

Tipos de celda: `PARED`, `LIBRE`, `INICIO`, `SALIDA1`, `SALIDA2`.

### `gui.py`

Contiene la clase `MazeGUI`, que dibuja el laberinto en un `Canvas` de Tkinter y maneja:

- El movimiento manual del jugador con el teclado.
- El algoritmo recursivo `_explorar`, que recorre el laberinto completo con backtracking (avanza, marca la celda como visitada, prueba las 4 direcciones y retrocede si no hay más movimientos posibles), registrando cada paso para poder animarlo.
- La animación en dos fases: primero la exploración completa (con retorno al inicio) y luego el recorrido de la ruta más corta encontrada.
- La ventana de estadísticas con el resumen de la resolución.

### `test_laberinto.py`

Suite de tests con `unittest` que valida, sobre múltiples semillas aleatorias:

- Que no existan bloques 2x2 de celdas libres ni paredes completamente aisladas.
- Que ambas salidas sean alcanzables desde el inicio (verificado con BFS).
- Que la posición de las salidas varíe entre distintas semillas.
- Que el algoritmo recursivo de backtracking recorra cada celda transitable exactamente una vez, que la cantidad de avances y retrocesos coincida, y que encuentre correctamente la ruta óptima hacia alguna de las dos salidas.

## ▶Cómo ejecutar

Requisitos: Python 3 con Tkinter (incluido por defecto en la mayoría de las instalaciones estándar de Python).

```bash
python main.py
```

Controles:

- **Flechas** o **WASD**: mover al jugador.
- **Nuevo laberinto**: genera un laberinto nuevo.
- **Resolver automático**: dispara la exploración recursiva y la animación del camino óptimo.
- **Detener**: corta la animación en curso y muestra el resultado final.
- **Ver Estadísticas**: abre una ventana con el detalle de la última resolución automática.

## Cómo correr los tests

```bash
python -m unittest test_laberinto.py
```

## Sobre el algoritmo

El corazón del trabajo práctico es la función recursiva de exploración (`_explorar` en `gui.py`, replicada en los tests como `explorar`):

1. **Caso base**: si la celda no es transitable, o ya fue visitada, la recursión corta ahí.
2. **Avance**: marca la celda como visitada, la agrega al camino actual y, si es una salida, guarda esa ruta como una solución posible.
3. **Llamada recursiva**: se invoca a sí misma para cada una de las 4 direcciones vecinas transitables y no visitadas.
4. **Retroceso (backtracking)**: cuando ya no hay movimientos posibles desde una celda, se la quita del camino actual y la recursión retrocede hacia la llamada anterior, hasta volver por completo al punto de partida.

Al finalizar, se comparan todas las rutas encontradas hacia las salidas y se elige la de menor cantidad de pasos como solución óptima, que luego se anima sobre el canvas.