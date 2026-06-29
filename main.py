from pathlib import Path
import ctypes
import math

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
        pg.display.set_caption("Circuit Cube - 3 caras")
        self.clock = pg.time.Clock()

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader = create_shader(
            ROOT / "shaders" / "vertex.glsl",
            ROOT / "shaders" / "fragment.glsl",
        )
        glUseProgram(self.shader)

        self.faces = [
            Face((0.0, 0.0), 1.0, LEFT_FACE),
            Face((0.0, 0.0), 1.0, RIGHT_FACE),
            Face((0.0, 0.0), 1.0, TOP_FACE),
        ]

        self.textures = CircuitTextures()

        glUniform1i(glGetUniformLocation(self.shader, "textureLeft"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "textureRight"), 1)
        glUniform1i(glGetUniformLocation(self.shader, "textureTop"), 2)

        self.cube_vertices = self.create_cube_vertices()
        self.update_warps()
        self.edge_shader = create_color_shader()
        self.edges = CubeEdges(cube_edge_segments(self.cube_vertices), self.edge_shader)

    def create_cube_vertices(self):
        # Seven visible cube vertices. The three vectors from v3 have
        # equivalent projected length, so each face starts as a unit square
        # and appears as a joined cube face after the homography.
        return {
            "v1": (-0.52, 0.30),
            "v2": (-0.52, -0.30),
            "v3": (0.0, 0.0),
            "v4": (0.0, -0.60),
            "v5": (0.52, 0.30),
            "v6": (0.52, -0.30),
            "v7": (0.0, 0.60),
        }

    def update_warps(self):
        v1 = self.cube_vertices["v1"]
        v2 = self.cube_vertices["v2"]
        v3 = self.cube_vertices["v3"]
        v4 = self.cube_vertices["v4"]
        v5 = self.cube_vertices["v5"]
        v6 = self.cube_vertices["v6"]
        v7 = self.cube_vertices["v7"]

        face_targets = [
            (v2, v4, v3, v1),
            (v4, v6, v5, v3),
            (v3, v5, v7, v1),
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
            self.textures.update(pg.time.get_ticks() / 1000.0)
            self.textures.use()

            for face in self.faces:
                face.draw()

            self.edges.draw()

            pg.display.flip()
            self.clock.tick(60)

        self.destroy()

    def destroy(self):
        for face in self.faces:
            face.destroy()
        self.edges.destroy()
        self.textures.destroy()
        glDeleteProgram(self.edge_shader)
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


class CubeEdges:
    def __init__(self, segments, shader):
        self.shader = shader
        vertices = []
        for start, end in segments:
            vertices.extend([start[0], start[1], end[0], end[1]])
        self.vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(self.vertices) // 2

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * self.vertices.itemsize, ctypes.c_void_p(0))

    def draw(self):
        glUseProgram(self.shader)
        glUniform4f(glGetUniformLocation(self.shader, "lineColor"), 0.02, 0.02, 0.02, 1.0)
        glLineWidth(3)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class CircuitTextures:
    def __init__(self):
        paper = (252, 252, 250)
        blue = (62, 70, 211)
        pulse = (255, 218, 24)
        pulse_soft = (255, 236, 88)
        self.faces = [
            SingleLineFace(
                paper,
                blue,
                pulse,
                pulse_soft,
                [
                    (0.00, 0.50),
                    (1.00, 0.50),
                ],
                (0.00, 0.33),
            ),
            SingleLineFace(
                paper,
                blue,
                pulse,
                pulse_soft,
                [
                    (0.00, 0.50),
                    (0.54, 0.50),
                    (0.54, 0.00),
                ],
                (0.33, 0.66),
            ),
            SingleLineFace(
                paper,
                blue,
                pulse,
                pulse_soft,
                [
                    (0.54, 1.00),
                    (0.54, 0.00),
                ],
                (0.66, 1.00),
            ),
        ]

        self.texture_left = create_dynamic_texture(self.faces[0].surface)
        self.texture_right = create_dynamic_texture(self.faces[1].surface)
        self.texture_top = create_dynamic_texture(self.faces[2].surface)
        self.texture_ids = [self.texture_left, self.texture_right, self.texture_top]

    def update(self, elapsed):
        global_progress = (elapsed * 0.16) % 1.0
        for texture_id, face in zip(self.texture_ids, self.faces):
            face.draw(global_progress)
            update_dynamic_texture(texture_id, face.surface)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_left)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_right)

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.texture_top)

    def destroy(self):
        glDeleteTextures(3, (self.texture_left, self.texture_right, self.texture_top))


class SingleLineFace:
    def __init__(self, background, trace_color, pulse_color, pulse_soft_color, path, progress_range):
        self.size = 384
        self.surface = pg.Surface((self.size, self.size), pg.SRCALPHA)
        self.background = background
        self.trace_color = trace_color
        self.pulse_color = pulse_color
        self.pulse_soft_color = pulse_soft_color
        self.path = [self.to_pixels(point) for point in path]
        self.progress_start, self.progress_end = progress_range

    def to_pixels(self, point):
        x, y = point
        return int(x * (self.size - 1)), int(y * (self.size - 1))

    def draw(self, global_progress):
        self.surface.fill((*self.background, 255))
        self.draw_paper_texture()
        self.draw_trace()
        self.draw_pulse(global_progress)

    def draw_paper_texture(self):
        pass

    def draw_trace(self):
        if len(self.path) < 2:
            return
        shadow = (*mix_color(self.trace_color, (0, 0, 0), 0.35), 70)
        base = (*self.trace_color, 235)
        highlight = (*mix_color(self.trace_color, (255, 255, 255), 0.28), 210)
        pg.draw.lines(self.surface, shadow, False, self.path, 15)
        pg.draw.lines(self.surface, base, False, self.path, 11)
        pg.draw.lines(self.surface, highlight, False, self.path, 4)

    def draw_pulse(self, global_progress):
        if not self.progress_start <= global_progress < self.progress_end:
            return
        local_progress = (global_progress - self.progress_start) / (self.progress_end - self.progress_start)
        x, y, _ = point_and_angle_on_path(self.path, local_progress)
        position = (int(x), int(y))

        for radius, alpha in [(24, 24), (15, 72), (7, 235)]:
            pg.draw.circle(self.surface, (*self.pulse_soft_color, alpha), position, radius)
        pg.draw.circle(self.surface, (*self.pulse_color, 255), position, 5)

def create_dynamic_texture(surface):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    width, height = surface.get_size()
    data = pg.image.tobytes(surface, "RGBA", True)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    return texture


def update_dynamic_texture(texture, surface):
    glBindTexture(GL_TEXTURE_2D, texture)
    width, height = surface.get_size()
    data = pg.image.tobytes(surface, "RGBA", True)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)


def point_and_angle_on_path(path, progress):
    lengths = []
    total = 0.0
    for start, end in zip(path, path[1:]):
        length = math.dist(start, end)
        lengths.append(length)
        total += length

    target = progress * total
    travelled = 0.0
    for (start, end), length in zip(zip(path, path[1:]), lengths):
        if travelled + length >= target:
            local = 0.0 if length == 0.0 else (target - travelled) / length
            x = start[0] + (end[0] - start[0]) * local
            y = start[1] + (end[1] - start[1]) * local
            angle = math.atan2(end[1] - start[1], end[0] - start[0])
            return x, y, angle
        travelled += length

    start, end = path[-2], path[-1]
    return path[-1][0], path[-1][1], math.atan2(end[1] - start[1], end[0] - start[0])


def mix_color(color_a, color_b, amount):
    return tuple(int(a + (b - a) * amount) for a, b in zip(color_a, color_b))


def cube_edge_segments(vertices):
    names = [
        ("v1", "v2"),
        ("v2", "v4"),
        ("v4", "v6"),
        ("v6", "v5"),
        ("v5", "v7"),
        ("v7", "v1"),
        ("v1", "v3"),
        ("v3", "v5"),
        ("v3", "v4"),
    ]
    return [(vertices[start], vertices[end]) for start, end in names]


def create_shader(vertex_path, fragment_path):
    vertex_src = vertex_path.read_text(encoding="utf-8")
    fragment_src = fragment_path.read_text(encoding="utf-8")

    return compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )


def create_color_shader():
    vertex_src = """
    #version 330 core

    layout (location = 0) in vec2 position;

    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
    }
    """
    fragment_src = """
    #version 330 core

    uniform vec4 lineColor;
    out vec4 color;

    void main()
    {
        color = lineColor;
    }
    """

    return compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )


if __name__ == "__main__":
    App().run()
