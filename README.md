# Cubo base con 3 caras

Base minima para replicar el proyecto: renderiza un cubo aparente usando tres caras 2D texturizadas: `arriba`, `izquierda` y `derecha`.

El cubo no es un modelo 3D real. Cada cara es un cuadrado formado por dos triangulos, y luego cada cuadrado se deforma con una homografia para que visualmente parezca una cara del cubo.

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
- `img/arriba`, `img/izquierda`, `img/derecha`: carpetas donde puedes poner una imagen `default.png` para cada cara.
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

## Texturas

Puedes agregar tus propias imagenes asi:

```text
img/arriba/default.png
img/izquierda/default.png
img/derecha/default.png
```

Si no existen esas imagenes, el programa genera texturas simples de colores automaticamente para que igual puedas ver el cubo.

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
