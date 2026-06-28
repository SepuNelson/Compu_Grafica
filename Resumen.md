# Resumen del proyecto `audiocx/proyecto-inf451`

Repositorio original: <https://github.com/audiocx/proyecto-inf451.git>

Este proyecto corresponde a un trabajo de Computacion Grafica de la USM, semestre 2023-1. Su objetivo principal es mostrar un cubo interactivo con texturas, usando Python, Pygame, OpenGL y shaders GLSL.

## Proposito del proyecto

El programa renderiza una figura que visualmente parece un cubo con tres caras visibles. Sin embargo, tecnicamente no construye un cubo 3D completo con camara, profundidad, luces o matriz de proyeccion. En vez de eso, dibuja tres cuadrados 2D texturizados y los deforma mediante transformaciones proyectivas, tambien llamadas homografias, para simular las caras visibles de un cubo.

El usuario puede mover los vertices del cubo con el mouse, cambiar el vertice seleccionado con el teclado y activar un modo de colores dinamicos.

## Lenguaje y tecnologias

El lenguaje principal es Python.

Tambien se usan shaders escritos en GLSL, especificamente con `#version 330 core`.

Las dependencias principales son:

- `pygame`: crea la ventana, maneja eventos de teclado y mouse, y carga imagenes.
- `PyOpenGL`: permite usar OpenGL desde Python.
- `PyOpenGL_accelerate`: mejora el rendimiento de PyOpenGL.
- `numpy`: se usa para trabajar con matrices y resolver sistemas lineales.
- `ctypes`: se usa para indicar offsets de memoria en los atributos de vertices de OpenGL.

No usa frameworks web, Unity, Blender, Three.js ni un motor 3D externo.

## Estructura del proyecto

Los archivos principales son:

- `main.py`: contiene la aplicacion principal, la inicializacion de Pygame/OpenGL, el loop de renderizado, la carga de texturas y las clases principales.
- `warp.py`: calcula la matriz de transformacion proyectiva para deformar cada cara.
- `shaders/vertex.txt`: vertex shader activo. Transforma los vertices de cada cara.
- `shaders/fragmentTex.txt`: fragment shader activo. Aplica las texturas a cada cara.
- `shaders/vertex1.txt` y `shaders/fragment.txt`: parecen archivos antiguos o pruebas; no son los shaders usados por el flujo principal.
- `img/A`, `img/B`, `img/C`: contienen las texturas de las tres caras visibles del cubo.
- `img/grass.jpg` e `img/chess.png`: estan en el repositorio, pero no se usan en `main.py`.

## Arquitectura general

La arquitectura esta concentrada principalmente en `main.py`.

### Clase `App`

Es la clase principal del programa. Se encarga de:

- Inicializar Pygame.
- Crear una ventana OpenGL de `1280x720`.
- Compilar y activar los shaders.
- Crear las tres caras visibles del cubo.
- Cargar los sets de texturas.
- Manejar eventos de teclado y mouse.
- Ejecutar el loop principal de renderizado.
- Liberar recursos al cerrar el programa.

### Clase `Square`

Representa una cara cuadrada. Cada cara se construye con dos triangulos, es decir, seis vertices.

Cada vertice contiene cinco valores:

```text
x, y, flag, tex_u, tex_v
```

Donde:

- `x`, `y`: posicion base del vertice.
- `flag`: indica a que cara pertenece el vertice.
- `tex_u`, `tex_v`: coordenadas de textura.

Los valores de `flag` son:

- `0`: cara A.
- `1`: cara B.
- `2`: cara C.

### Clase `Textures`

Carga tres imagenes por cada personaje o textura: una para la cara A, otra para la cara B y otra para la cara C.

Luego crea tres texturas OpenGL y las asigna a:

- `GL_TEXTURE0`
- `GL_TEXTURE1`
- `GL_TEXTURE2`

Estas texturas se conectan con los uniforms del fragment shader:

- `imageTextureA`
- `imageTextureB`
- `imageTextureC`

### Archivo `warp.py`

Contiene la funcion `MatrixT`. Esta funcion calcula los 8 coeficientes de una homografia.

Una homografia permite transformar un cuadrado original en un cuadrilatero arbitrario. Esto es lo que hace que las caras planas parezcan formar un cubo.

La funcion arma un sistema lineal y lo resuelve con:

```python
np.linalg.solve(A, b)
```

## Como se renderiza el cubo

El cubo se renderiza como tres caras planas:

- Cara A: sur-oeste.
- Cara B: sur-este.
- Cara C: norte.

Cada cara parte como un cuadrado simple. Luego, antes de ser dibujada, el vertex shader aplica una transformacion proyectiva distinta para ubicarla en la posicion deformada correspondiente.

La transformacion usada tiene esta forma:

```glsl
u = (c[0]*x + c[1]*y + c[2]) / (c[6]*x + c[7]*y + 1);
v = (c[3]*x + c[4]*y + c[5]) / (c[6]*x + c[7]*y + 1);
```

Luego se asigna:

```glsl
gl_Position = vec4(u, v, 0.0, 1.0);
```

Esto significa que la posicion final del vertice se calcula directamente en el shader.

Despues, el fragment shader revisa el `flag` de la cara y decide que textura usar:

- Si `flag == 0`, usa `imageTextureA`.
- Si `flag == 1`, usa `imageTextureB`.
- Si `flag == 2`, usa `imageTextureC`.

Finalmente, el color final del pixel es la textura multiplicada por un color de la cara. Ese color puede ser blanco normal o un color dinamico si esta activo el modo disco.

## Como se renderizan las imagenes

Las imagenes se cargan con Pygame:

```python
image = pg.image.load(file).convert_alpha()
```

Luego se convierten a datos RGBA:

```python
img_data = pg.image.tostring(image, 'RGBA')
```

Y finalmente se suben a la GPU con OpenGL:

```python
glTexImage2D(...)
```

El programa usa filtros de textura:

- `GL_NEAREST` para minificacion.
- `GL_LINEAR` para magnificacion.

Tambien llama a:

```python
glGenerateMipmap(GL_TEXTURE_2D)
```

## Loop principal

El loop principal hace lo siguiente en cada frame:

1. Revisa eventos de Pygame.
2. Si se presiona una tecla entre `0` y `6`, cambia el vertice seleccionado.
3. Si se hace click, mueve el vertice seleccionado a la posicion del mouse.
4. Recalcula las homografias de las caras.
5. Cambia de textura cada 100 frames aproximadamente.
6. Si esta activo el modo disco, cambia los colores con funciones seno y coseno.
7. Limpia la pantalla con `glClear`.
8. Dibuja las tres caras con `glDrawArrays`.
9. Actualiza la ventana con `pg.display.flip()`.
10. Limita la ejecucion a 60 FPS con `self.clock.tick(60)`.

## Controles

Los controles del programa son:

- `0`: selecciona el vertice central.
- `1`: selecciona el vertice mas al sur-oeste de la cara A.
- `2` a `6`: seleccionan los siguientes vertices en sentido antihorario.
- Click izquierdo: mueve el vertice seleccionado a la posicion del mouse.
- `D`: activa o desactiva el modo disco.

## Como ejecutar el programa

Primero se deben instalar las dependencias:

```powershell
python -m pip install PyOpenGL PyOpenGL_accelerate pygame numpy
```

Luego se debe entrar a la carpeta del proyecto, donde esta `main.py`:

```powershell
cd C:\Users\Nelson\Downloads\Compu_Grafica\proyecto-inf451-src
```

Y ejecutar:

```powershell
python main.py
```

Tambien podria funcionar con:

```powershell
python3 main.py
```

Es importante ejecutar el programa desde la carpeta donde esta `main.py`, porque las rutas a `shaders` e `img` son relativas.

## Que se ve al ejecutar

Al ejecutar el programa se abre una ventana de Pygame con OpenGL. En la ventana se ven tres caras texturizadas que forman visualmente un cubo.

Cada cierto tiempo cambia el set de texturas, por ejemplo entre personajes como:

- Alex
- Cow
- Creeper
- Husk
- RedCow
- Skeleton
- Steve
- WitherSkeleton
- Zombie

El usuario puede deformar el cubo moviendo sus vertices con el mouse.

## Aspectos importantes para replicarlo

Para replicar este proyecto, lo mas importante es entender estas ideas:

- La figura no es un cubo 3D real, sino una simulacion 2D mediante tres caras deformadas.
- Cada cara es un cuadrado formado por dos triangulos.
- La deformacion se calcula en Python usando una homografia.
- Los coeficientes de la homografia se envian al vertex shader como uniforms.
- El vertex shader transforma los vertices.
- El fragment shader aplica la textura correcta segun la cara.
- Las imagenes estan separadas en carpetas `A`, `B` y `C`, porque cada cara necesita su propia textura.

## Posibles mejoras o detalles fragiles

El proyecto funciona como demostracion, pero tiene algunos puntos mejorables:

- No incluye `requirements.txt`.
- No tiene instrucciones detalladas de instalacion por sistema operativo.
- Incluye archivos `__pycache__`, que normalmente no deberian estar versionados.
- Hay shaders no usados, lo que puede confundir al leer el proyecto.
- La clase `Material` existe, pero no se usa en el flujo principal.
- El cubo no usa profundidad, iluminacion ni camara 3D.
- En `main.py`, los colores `colorA`, `colorB` y `colorC` se envian con `glUniform1fv(..., 8, ...)`, aunque son arrays de 3 valores. Lo mas correcto seria usar 3 o `glUniform3fv`.

## Conclusion

El proyecto es una aplicacion grafica interactiva en Python que usa OpenGL moderno con shaders para mostrar tres caras texturizadas simulando un cubo. Su parte mas interesante es el uso de homografias para deformar cuadrados y convertirlos visualmente en caras de un cubo manipulable.

Para replicarlo, se debe implementar una ventana OpenGL, cargar texturas, crear tres cuadrados, calcular una transformacion proyectiva por cara y aplicar esa transformacion en el vertex shader.
