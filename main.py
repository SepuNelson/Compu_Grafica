from pathlib import Path
import ctypes

import numpy as np
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from warp import homography_coefficients


ROOT = Path(__file__).resolve().parent
WIDTH = 1000
HEIGHT = 700

LEFT_FACE = 0
RIGHT_FACE = 1
TOP_FACE = 2


class App:
    def __init__(self):
        pg.init()
        pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_caption("Cubo base - 3 caras")
        self.clock = pg.time.Clock()

        glClearColor(0.06, 0.07, 0.09, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader = create_shader(
            ROOT / "shaders" / "vertex.glsl",
            ROOT / "shaders" / "fragment.glsl",
        )
        glUseProgram(self.shader)

        self.faces = [
            Face((-0.90, -0.90), 0.80, LEFT_FACE),
            Face((0.10, -0.90), 0.80, RIGHT_FACE),
            Face((-0.90, 0.10), 0.80, TOP_FACE),
        ]

        self.textures = CubeTextures(
            ROOT / "img" / "izquierda" / "default.png",
            ROOT / "img" / "derecha" / "default.png",
            ROOT / "img" / "arriba" / "default.png",
        )

        glUniform1i(glGetUniformLocation(self.shader, "textureLeft"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "textureRight"), 1)
        glUniform1i(glGetUniformLocation(self.shader, "textureTop"), 2)

        self.update_warps()

    def update_warps(self):
        center = (0.0, 0.0)
        left_bottom = (-0.46, -0.36)
        bottom = (0.0, -0.76)
        right_bottom = (0.46, -0.36)
        right_top = (0.46, 0.28)
        top = (0.0, 0.58)
        left_top = (-0.46, 0.28)

        face_targets = [
            (left_bottom, bottom, center, left_top),
            (bottom, right_bottom, right_top, center),
            (left_top, center, right_top, top),
        ]
        uniform_names = ["warpLeft", "warpRight", "warpTop"]

        for face, points, uniform_name in zip(self.faces, face_targets, uniform_names):
            coeffs = homography_coefficients(face.origin, face.size, *points)
            location = glGetUniformLocation(self.shader, uniform_name)
            glUniform1fv(location, 8, coeffs)

    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)
            self.textures.use()

            for face in self.faces:
                face.draw()

            pg.display.flip()
            self.clock.tick(60)

        self.destroy()

    def destroy(self):
        for face in self.faces:
            face.destroy()
        self.textures.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class Face:
    def __init__(self, origin, size, face_id):
        self.origin = origin
        self.size = size
        x0, y0 = origin
        x1, y1 = x0 + size, y0 + size

        vertices = [
            x0, y0, face_id, 0.0, 0.0,
            x1, y0, face_id, 1.0, 0.0,
            x1, y1, face_id, 1.0, 1.0,
            x1, y1, face_id, 1.0, 1.0,
            x0, y1, face_id, 0.0, 1.0,
            x0, y0, face_id, 0.0, 0.0,
        ]
        self.vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        stride = 5 * self.vertices.itemsize
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(3 * self.vertices.itemsize),
        )

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class CubeTextures:
    def __init__(self, left_path, right_path, top_path):
        self.texture_left = load_texture(left_path, (90, 142, 255), (18, 36, 80))
        self.texture_right = load_texture(right_path, (255, 186, 73), (91, 48, 12))
        self.texture_top = load_texture(top_path, (92, 220, 154), (18, 72, 44))

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_left)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_right)

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.texture_top)

    def destroy(self):
        glDeleteTextures(3, (self.texture_left, self.texture_right, self.texture_top))


def load_texture(path, color_a, color_b):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    if path.exists():
        surface = pg.image.load(path).convert_alpha()
    else:
        surface = make_checker_surface(color_a, color_b)

    width, height = surface.get_size()
    data = pg.image.tostring(surface, "RGBA", True)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glGenerateMipmap(GL_TEXTURE_2D)
    return texture


def make_checker_surface(color_a, color_b):
    size = 128
    tile = 16
    surface = pg.Surface((size, size), pg.SRCALPHA)
    for y in range(0, size, tile):
        for x in range(0, size, tile):
            color = color_a if ((x // tile) + (y // tile)) % 2 == 0 else color_b
            pg.draw.rect(surface, color, (x, y, tile, tile))
    return surface


def create_shader(vertex_path, fragment_path):
    vertex_src = vertex_path.read_text(encoding="utf-8")
    fragment_src = fragment_path.read_text(encoding="utf-8")

    return compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )


if __name__ == "__main__":
    App().run()
