import math

import pygame as pg
from OpenGL.GL import *


ANIMATION_SPEED = 0.16
MIN_ANIMATION_SPEED = 0.04
MAX_ANIMATION_SPEED = 0.64
SPEED_FACTOR = 1.25
TEXTURE_SIZE = 384

PANEL_COLOR = (6, 10, 24)
NEON_BLUE = (34, 195, 255)
RED_BALL = (255, 42, 54)
RED_GLOW = (255, 92, 92)
GREEN_BALL = (42, 255, 126)
GREEN_GLOW = (108, 255, 166)
YELLOW_BALL = (255, 218, 48)
YELLOW_GLOW = (255, 236, 116)

BALL_COLOR_STATES = [
    (RED_BALL, RED_GLOW),
    (GREEN_BALL, GREEN_GLOW),
    (YELLOW_BALL, YELLOW_GLOW),
]


def arc_points(center, radius, start_degrees, end_degrees, steps):
    points = []
    for index in range(steps + 1):
        t = index / steps
        degrees = start_degrees + (end_degrees - start_degrees) * t
        radians = math.radians(degrees)
        points.append((
            center[0] + math.cos(radians) * radius,
            center[1] + math.sin(radians) * radius,
        ))
    return points


LEFT_FACE_PIECES = [
    (
        [
            (0.84, 0.00),
            (0.84, 0.24),
            (0.52, 0.25),
            (0.12, 0.24),
            (0.12, 0.00),
        ],
        (0.64, 0.82),
    ),
    (
        [
            (0.50, 1.00),
            (0.50, 0.56),
            (1.00, 0.56),
        ],
        (0.00, 0.17),
    ),
]

RIGHT_FACE_PIECES = [
    (
        [
            (0.00, 0.56),
            (0.20, 0.56),
        ]
        + arc_points((0.50, 0.56), 0.30, 180, -90, 40)[1:]
        + [
            (0.50, 0.00),
        ],
        (0.17, 0.52),
    ),
]

TOP_FACE_PIECES = [
    (
        [
            (0.50, 1.00),
            (0.50, 0.84),
            (0.00, 0.84),
        ],
        (0.52, 0.64),
    ),
    (
        [
            (0.00, 0.12),
            (0.50, 0.12),
            (0.50, 0.50),
            (1.00, 0.50),
        ],
        (0.82, 1.00),
    ),
]

FACE_DESIGNS = [
    LEFT_FACE_PIECES,
    RIGHT_FACE_PIECES,
    TOP_FACE_PIECES,
]


class CircuitTextures:
    def __init__(self):
        self.animation_speed = ANIMATION_SPEED
        self.progress = 0.0
        self.last_elapsed = None
        self.ball_color_index = 0
        self.faces = [
            SingleLineFace(PANEL_COLOR, NEON_BLUE, RED_BALL, RED_GLOW, pieces)
            for pieces in FACE_DESIGNS
        ]

        self.texture_left = create_dynamic_texture(self.faces[0].surface)
        self.texture_right = create_dynamic_texture(self.faces[1].surface)
        self.texture_top = create_dynamic_texture(self.faces[2].surface)
        self.texture_ids = [self.texture_left, self.texture_right, self.texture_top]

    def update(self, elapsed):
        if self.last_elapsed is None:
            self.last_elapsed = elapsed

        delta = max(0.0, elapsed - self.last_elapsed)
        self.last_elapsed = elapsed
        self.progress = (self.progress + delta * self.animation_speed) % 1.0

        for texture_id, face in zip(self.texture_ids, self.faces):
            face.draw(self.progress)
            update_dynamic_texture(texture_id, face.surface)

    def cycle_ball_color(self):
        self.ball_color_index = (self.ball_color_index + 1) % len(BALL_COLOR_STATES)
        pulse_color, pulse_soft_color = BALL_COLOR_STATES[self.ball_color_index]
        for face in self.faces:
            face.set_pulse_colors(pulse_color, pulse_soft_color)

    def speed_up(self):
        self.animation_speed = min(MAX_ANIMATION_SPEED, self.animation_speed * SPEED_FACTOR)

    def slow_down(self):
        self.animation_speed = max(MIN_ANIMATION_SPEED, self.animation_speed / SPEED_FACTOR)

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
    def __init__(self, background, trace_color, pulse_color, pulse_soft_color, pieces):
        self.size = TEXTURE_SIZE
        self.surface = pg.Surface((self.size, self.size), pg.SRCALPHA)
        self.background = background
        self.trace_color = trace_color
        self.pulse_color = pulse_color
        self.pulse_soft_color = pulse_soft_color
        self.pieces = [
            ([self.to_pixels(point) for point in path], progress_range)
            for path, progress_range in pieces
        ]

    def set_pulse_colors(self, pulse_color, pulse_soft_color):
        self.pulse_color = pulse_color
        self.pulse_soft_color = pulse_soft_color

    def to_pixels(self, point):
        x, y = point
        return int(x * (self.size - 1)), int(y * (self.size - 1))

    def draw(self, global_progress):
        self.surface.fill((*self.background, 255))
        self.draw_paper_texture()
        self.draw_trace()
        self.draw_active_trace(global_progress)
        self.draw_pulse(global_progress)

    def draw_paper_texture(self):
        grid_minor = (28, 58, 88, 52)
        grid_major = (44, 118, 168, 70)
        for pos in range(0, self.size + 1, 32):
            color = grid_major if pos % 128 == 0 else grid_minor
            pg.draw.line(self.surface, color, (pos, 0), (pos, self.size), 1)
            pg.draw.line(self.surface, color, (0, pos), (self.size, pos), 1)

    def draw_trace(self):
        layers = [
            ((*self.trace_color, 22), 34),
            ((*self.trace_color, 46), 24),
            ((*mix_color(self.trace_color, (120, 235, 255), 0.35), 90), 15),
            ((*self.trace_color, 150), 8),
            ((*mix_color(self.trace_color, (255, 255, 255), 0.45), 170), 3),
        ]
        for path, _ in self.pieces:
            if len(path) < 2:
                continue
            for color, width in layers:
                self.draw_rounded_path(path, color, width)

    def draw_active_trace(self, global_progress):
        layers = [
            ((*self.trace_color, 60), 46),
            ((*self.trace_color, 110), 31),
            ((*mix_color(self.trace_color, (130, 240, 255), 0.45), 190), 20),
            ((*self.trace_color, 255), 12),
            ((*mix_color(self.trace_color, (255, 255, 255), 0.66), 255), 5),
        ]

        for path, (progress_start, progress_end) in self.pieces:
            if global_progress >= progress_end:
                traced_path = path
            elif progress_start <= global_progress < progress_end:
                local_progress = (global_progress - progress_start) / (progress_end - progress_start)
                traced_path = partial_path(path, local_progress)
            else:
                continue

            if len(traced_path) < 2:
                continue

            for color, width in layers:
                self.draw_rounded_path(traced_path, color, width)

    def draw_rounded_path(self, path, color, width):
        pg.draw.lines(self.surface, color, False, path, width)
        radius = max(1, width // 2)
        for point in path:
            pg.draw.circle(self.surface, color, point, radius)

    def draw_pulse(self, global_progress):
        active_piece = self.get_active_piece(global_progress)
        if active_piece is None:
            return

        path, progress_start, progress_end = active_piece
        local_progress = (global_progress - progress_start) / (progress_end - progress_start)
        x, y, _ = point_and_angle_on_path(path, local_progress)
        position = (int(x), int(y))

        for radius, alpha in [(38, 32), (26, 76), (15, 170)]:
            pg.draw.circle(self.surface, (*self.pulse_soft_color, alpha), position, radius)
        pg.draw.circle(self.surface, (*self.pulse_color, 255), position, 9)
        pg.draw.circle(self.surface, (255, 230, 230, 230), (position[0] - 3, position[1] - 3), 3)

    def get_active_piece(self, global_progress):
        for path, (progress_start, progress_end) in self.pieces:
            if progress_start <= global_progress < progress_end:
                return path, progress_start, progress_end
        return None


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


def partial_path(path, progress):
    if len(path) < 2:
        return path

    lengths = []
    total = 0.0
    for start, end in zip(path, path[1:]):
        length = math.dist(start, end)
        lengths.append(length)
        total += length

    target = progress * total
    travelled = 0.0
    result = [path[0]]

    for (start, end), length in zip(zip(path, path[1:]), lengths):
        if travelled + length < target:
            result.append(end)
            travelled += length
            continue

        local = 0.0 if length == 0.0 else (target - travelled) / length
        current = (
            start[0] + (end[0] - start[0]) * local,
            start[1] + (end[1] - start[1]) * local,
        )
        result.append(current)
        return result

    return path


def mix_color(color_a, color_b, amount):
    return tuple(int(a + (b - a) * amount) for a, b in zip(color_a, color_b))
