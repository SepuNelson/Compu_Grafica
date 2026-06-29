# Circuit Cube con 3 caras

Base minima para replicar el proyecto: renderiza un cubo aparente usando tres caras 2D: `arriba`, `izquierda` y `derecha`.

El cubo no es un modelo 3D real. Cada cara es un cuadrado formado por dos triangulos, y luego cada cuadrado se deforma con una homografia para que visualmente parezca una cara del cubo.

Cada cara parte como un cuadrado de lado `1.0`. Luego se proyecta sobre los vertices visibles del cubo para que las caras izquierda, derecha y superior compartan aristas.

Los vertices del cubo se calculan desde una longitud de arista en pixeles. Esto corrige el aspecto rectangular de la ventana OpenGL y permite que todas las aristas visibles se vean del mismo largo en pantalla.

Las aristas del cubo se dibujan como lineas OpenGL aparte, directamente entre los vertices compartidos. No forman parte de las texturas de cada cara, para evitar espacios visibles entre caras.

La version actual dibuja un circuito estilo neon por codigo: fondo oscuro, linea/tubo azul brillante y una pelota roja luminosa. Por ahora la cara izquierda y la cara superior tienen recorrido conectado; la cara derecha queda vacia para seguir construyendo el circuito por partes.

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

- Dibuja un fondo oscuro con una grilla tenue.
- Dibuja una linea/tubo azul con brillo neon.
- La cara izquierda tiene dos tramos inspirados en el boceto: uno superior con bajada, avance horizontal y subida al borde; y otro que entra desde el centro inferior, sube y gira hacia la derecha.
- La cara superior tiene dos trazos: uno parte desde el centro de la arista compartida con la cara derecha, sube una cuadricula hacia dentro y gira 90 grados para conectar con el trazo mas cercano de la cara izquierda; el otro nace desde el otro extremo de la cinta izquierda, avanza hasta la mitad, gira 90 grados hacia el centro y vuelve a girar 90 grados para tocar la arista opuesta.
- La cara derecha conecta la cinta de la cara izquierda con la cara superior mediante una entrada horizontal, una curva perfecta de 3/4 de circulo y una salida vertical.
- La pelota roja empieza en la cara izquierda, avanza por la cara derecha y termina en la cara superior siguiendo las conexiones reales de las aristas.
- La pista se ve de forma tenue y el tramo recorrido se ilumina detras de la pelota roja.
- Al terminar el recorrido conectado entre izquierda y arriba, el rastro se reinicia junto con la pelota.
- Anima una pelota roja luminosa que recorre los tramos definidos.
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
