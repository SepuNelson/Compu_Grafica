# Proyecto 

Proyecto para la asigantura  "INF451 - Computación Gráfica", 

## Estructura

```text
Compu_Grafica/
|-- main.py
|-- cubo.py
|-- diseno.py
|-- warp.py
|-- requirements.txt
|-- README.md
`-- shaders/
    |-- vertex.glsl
    `-- fragment.glsl
```

## Que hace cada archivo

- `main.py`: punto de entrada del programa. Solo importa la app y la ejecuta.
- `cubo.py`: crea la ventana, inicializa OpenGL, define vertices, dimensiones del cubo, homografias, caras, aristas y shaders.
- `diseno.py`: define el diseno editable de la cinta, colores neon, rutas de cada cara, rangos de animacion, pelota roja y rastro.
- `warp.py`: calcula los coeficientes de homografia para deformar cada cara.
- `shaders/vertex.glsl`: transforma los vertices de cada cara hacia su posicion final.
- `shaders/fragment.glsl`: aplica la textura correspondiente a cada cara.
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

El circuito se genera dentro de `diseno.py` usando superficies de Pygame. No necesita videos ni imagenes externas.

En cada frame el programa:

- Dibuja un fondo oscuro con una grilla tenue.
- Dibuja una linea/tubo azul con brillo neon.
- La cara izquierda tiene dos tramos inspirados en el boceto: uno superior con bajada, avance horizontal y subida al borde; y otro que entra desde el centro inferior, sube y gira hacia la derecha.
- La cara superior tiene dos trazos: uno parte desde el centro de la arista compartida con la cara derecha, sube una cuadricula hacia dentro y gira 90 grados para conectar con el trazo mas cercano de la cara izquierda; el otro nace desde el otro extremo de la cinta izquierda, avanza hasta la mitad, gira 90 grados hacia el centro y vuelve a girar 90 grados para tocar la arista opuesta.
- La cara derecha conecta la cinta de la cara izquierda con la cara superior mediante una entrada horizontal, una curva perfecta de 3/4 de circulo y una salida vertical.
- La pelota roja empieza en la cara izquierda, avanza por la cara derecha y termina en la cara superior siguiendo las conexiones reales de las aristas.
- La pista se ve de forma tenue y el tramo recorrido se ilumina detras de la pelota roja.
- Al terminar el recorrido completo por izquierda, derecha y arriba, el rastro se reinicia junto con la pelota.
- Anima una pelota roja luminosa que recorre los tramos definidos.
- Sube esas superficies a OpenGL como texturas dinamicas.

## Donde editar

- Dimensiones de ventana y cubo: `cubo.py`, constantes `WIDTH`, `HEIGHT` y `EDGE_PIXELS`.
- Forma/proyeccion del cubo: `cubo.py`, metodo `create_cube_vertices` y lista `face_targets`.
- Interaccion de vertices movibles: `cubo.py`, metodos `pick_vertex`, `move_vertex` y `mouse_to_ndc`.
- Diseno de la cinta: `diseno.py`, listas `LEFT_FACE_PIECES`, `RIGHT_FACE_PIECES` y `TOP_FACE_PIECES`.
- Colores, pelota y velocidad: `diseno.py`, constantes `PANEL_COLOR`, `NEON_BLUE`, `RED_BALL`, `RED_GLOW` y `ANIMATION_SPEED`.

## Controles

- Click izquierdo cerca de una interseccion natural de aristas y arrastrar: mover ese vertice del cubo.
- `Enter`: cambiar el color de la pelota en ciclo rojo, verde, amarillo y rojo.
- `Espacio`: aumentar la velocidad de la pelota.
- `Backspace`: disminuir la velocidad de la pelota.
- `F11`: alternar entre ventana normal y pantalla completa.
- `Esc`: cerrar la ventana.
- La ventana se puede redimensionar o maximizar.
- Cerrar la ventana desde la `X` tambien termina el programa.

## Idea tecnica

Cada cara parte como un cuadrado normal. Luego se calcula una homografia que transforma ese cuadrado en un cuadrilatero:

- cara izquierda
- cara derecha
- cara superior

Los coeficientes de cada homografia se envian al vertex shader. El shader usa esos coeficientes para calcular la posicion final de cada vertice.

La textura se elige en el fragment shader segun el identificador de la cara.
