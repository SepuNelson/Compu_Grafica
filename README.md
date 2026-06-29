# Circuit Cube con 3 caras

Base minima para replicar el proyecto: renderiza un cubo aparente usando tres caras 2D: `arriba`, `izquierda` y `derecha`.

El cubo no es un modelo 3D real. Cada cara es un cuadrado formado por dos triangulos, y luego cada cuadrado se deforma con una homografia para que visualmente parezca una cara del cubo.

La version actual dibuja un circuito muy simple por codigo: fondo blanco, una sola linea azul por tramos, conectada entre las tres caras, y un pulso que recorre el camino.

## Estructura

```text
Compu_Grafica/
|-- main.py
|-- warp.py
|-- requirements.txt
|-- README.md
|-- shaders/
|   |-- vertex.glsl
|   `-- fragment.glsl
`-- img/
    |-- arriba/
    |   `-- .gitkeep
    |-- izquierda/
    |   `-- .gitkeep
    `-- derecha/
        `-- .gitkeep
```

## Que hace cada archivo

- `main.py`: crea la ventana, inicializa OpenGL, carga shaders, crea las tres caras, carga texturas y dibuja el cubo.
- `warp.py`: calcula los coeficientes de homografia para deformar cada cara.
- `shaders/vertex.glsl`: transforma los vertices de cada cara hacia su posicion final.
- `shaders/fragment.glsl`: aplica la textura correspondiente a cada cara.
- `img/arriba`, `img/izquierda`, `img/derecha`: carpetas reservadas si despues quieres agregar recursos externos.
- `requirements.txt`: dependencias necesarias.

## Instalacion

Abre una terminal en esta carpeta:

```powershell
cd C:\Users\Nelson\Downloads\Compu_Grafica
```

Crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

Ejecuta el programa:

```powershell
python main.py
```

## Circuito animado

El circuito se genera dentro de `main.py` usando superficies de Pygame. No necesita videos ni imagenes externas.

En cada frame el programa:

- Dibuja el fondo claro de cada cara.
- Dibuja una sola linea azul.
- La cara izquierda tiene un tramo horizontal.
- La cara derecha continua el tramo horizontal y luego sube en 90 grados.
- La cara superior continua verticalmente desde esa conexion.
- Anima un pulso amarillo que recorre el camino completo.
- Sube esas superficies a OpenGL como texturas dinamicas.

## Controles

- `Esc`: cerrar la ventana.
- Cerrar la ventana desde la `X` tambien termina el programa.

## Idea tecnica

Cada cara parte como un cuadrado normal. Luego se calcula una homografia que transforma ese cuadrado en un cuadrilatero:

- cara izquierda
- cara derecha
- cara superior

Los coeficientes de cada homografia se envian al vertex shader. El shader usa esos coeficientes para calcular la posicion final de cada vertice.

La textura se elige en el fragment shader segun el identificador de la cara.
