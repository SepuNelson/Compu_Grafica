from pathlib import Path
import ctypes
import math

import numpy as np
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from diseno import CircuitTextures
from warp import homography_coefficients


ROOT = Path(__file__).resolve().parent
WIDTH = 1000
HEIGHT = 700
EDGE_PIXELS = 230.0
WINDOW_TITLE = "Circuit Cube - 3 caras"
HANDLE_RADIUS_PIXELS = 18

LEFT_FACE = 0
RIGHT_FACE = 1
TOP_FACE = 2


class App:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.window_width = WIDTH
        self.window_height = HEIGHT
        self.windowed_size = (WIDTH, HEIGHT)
        self.is_fullscreen = False
        self.dragged_vertex = None

        self.open_display(self.windowed_size, self.is_fullscreen)
        self.create_gl_resources()

    def open_display(self, size, fullscreen):
        flags = pg.OPENGL | pg.DOUBLEBUF
        if fullscreen:
            flags |= pg.FULLSCREEN
            surface = pg.display.set_mode((0, 0), flags)
        else:
            flags |= pg.RESIZABLE
            surface = pg.display.set_mode(size, flags)

        pg.display.set_caption(WINDOW_TITLE)
        self.window_width, self.window_height = surface.get_size()
        glViewport(0, 0, self.window_width, self.window_height)

    def create_gl_resources(self):
        glClearColor(0.01, 0.015, 0.03, 1.0)
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
        # OpenGL NDC is stretched by the window aspect ratio, so the cube
        # vertices are calculated from a desired visual edge length in pixels.
        half_width = self.window_width / 2.0
        half_height = self.window_height / 2.0
        edge_pixels = EDGE_PIXELS * min(self.window_width, self.window_height) / HEIGHT
        x = (edge_pixels * math.cos(math.radians(30.0))) / half_width
        y = (edge_pixels * math.sin(math.radians(30.0))) / half_height
        z = edge_pixels / half_height

        return {
            "v1": (-x, y),
            "v2": (-x, y - z),
            "v3": (0.0, 0.0),
            "v4": (0.0, -z),
            "v5": (x, y),
            "v6": (x, y - z),
            "v7": (0.0, 2.0 * y),
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
            if not np.all(np.isfinite(coeffs)):
                raise ValueError("Invalid face projection")
            location = glGetUniformLocation(self.shader, uniform_name)
            glUniform1fv(location, 8, coeffs)

    def mouse_to_ndc(self, position):
        x, y = position
        return (x / self.window_width) * 2.0 - 1.0, 1.0 - (y / self.window_height) * 2.0

    def ndc_to_screen(self, point):
        x, y = point
        return (x + 1.0) * self.window_width / 2.0, (1.0 - y) * self.window_height / 2.0

    def pick_vertex(self, position):
        closest_name = None
        closest_distance = HANDLE_RADIUS_PIXELS
        mx, my = position

        for name, point in self.cube_vertices.items():
            sx, sy = self.ndc_to_screen(point)
            distance = math.dist((mx, my), (sx, sy))
            if distance <= closest_distance:
                closest_name = name
                closest_distance = distance

        return closest_name

    def move_vertex(self, name, position):
        previous_position = self.cube_vertices[name]
        self.cube_vertices[name] = self.mouse_to_ndc(position)
        glUseProgram(self.shader)
        try:
            self.update_warps()
        except (np.linalg.LinAlgError, ValueError):
            self.cube_vertices[name] = previous_position
            self.update_warps()
            return

        self.edges.update_segments(cube_edge_segments(self.cube_vertices))

    def reset_cube_projection(self):
        self.cube_vertices = self.create_cube_vertices()
        glUseProgram(self.shader)
        self.update_warps()
        self.edges.update_segments(cube_edge_segments(self.cube_vertices))

    def resize_window(self, size):
        self.window_width = max(1, size[0])
        self.window_height = max(1, size[1])
        self.windowed_size = (self.window_width, self.window_height)
        glViewport(0, 0, self.window_width, self.window_height)
        self.dragged_vertex = None
        self.reset_cube_projection()

    def toggle_fullscreen(self):
        self.destroy_gl_resources()
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.windowed_size = (self.window_width, self.window_height)
            self.open_display((0, 0), fullscreen=True)
        else:
            self.open_display(self.windowed_size, fullscreen=False)

        self.dragged_vertex = None
        self.create_gl_resources()

    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.VIDEORESIZE and not self.is_fullscreen:
                    self.resize_window(event.size)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    elif event.key == pg.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pg.K_RETURN:
                        self.textures.cycle_ball_color()
                    elif event.key == pg.K_SPACE:
                        self.textures.speed_up()
                    elif event.key == pg.K_BACKSPACE:
                        self.textures.slow_down()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.dragged_vertex = self.pick_vertex(event.pos)
                if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.dragged_vertex = None
                if event.type == pg.MOUSEMOTION and self.dragged_vertex is not None:
                    self.move_vertex(self.dragged_vertex, event.pos)

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

    def destroy_gl_resources(self):
        for face in self.faces:
            face.destroy()
        self.edges.destroy()
        self.textures.destroy()
        glDeleteProgram(self.edge_shader)
        glDeleteProgram(self.shader)

    def destroy(self):
        self.destroy_gl_resources()
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
        self.vertices = self.segments_to_array(segments)
        self.vertex_count = len(self.vertices) // 2

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * self.vertices.itemsize, ctypes.c_void_p(0))

    def segments_to_array(self, segments):
        vertices = []
        for start, end in segments:
            vertices.extend([start[0], start[1], end[0], end[1]])
        return np.array(vertices, dtype=np.float32)

    def update_segments(self, segments):
        self.vertices = self.segments_to_array(segments)
        self.vertex_count = len(self.vertices) // 2
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

    def draw(self):
        glUseProgram(self.shader)
        glUniform4f(glGetUniformLocation(self.shader, "lineColor"), 0.45, 0.95, 1.0, 0.95)
        glLineWidth(2)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


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
