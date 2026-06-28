import numpy as np


def homography_coefficients(source_origin, source_size, p0, p1, p2, p3):
    """Return 8 homography coefficients mapping a source square to 4 points."""
    x0, y0 = source_origin
    x1, y1 = x0 + source_size, y0
    x2, y2 = x0 + source_size, y0 + source_size
    x3, y3 = x0, y0 + source_size

    u0, v0 = p0
    u1, v1 = p1
    u2, v2 = p2
    u3, v3 = p3

    matrix = np.array(
        [
            [x0, y0, 1, 0, 0, 0, -x0 * u0, -y0 * u0],
            [x1, y1, 1, 0, 0, 0, -x1 * u1, -y1 * u1],
            [x2, y2, 1, 0, 0, 0, -x2 * u2, -y2 * u2],
            [x3, y3, 1, 0, 0, 0, -x3 * u3, -y3 * u3],
            [0, 0, 0, x0, y0, 1, -x0 * v0, -y0 * v0],
            [0, 0, 0, x1, y1, 1, -x1 * v1, -y1 * v1],
            [0, 0, 0, x2, y2, 1, -x2 * v2, -y2 * v2],
            [0, 0, 0, x3, y3, 1, -x3 * v3, -y3 * v3],
        ],
        dtype=np.float32,
    )
    target = np.array([u0, u1, u2, u3, v0, v1, v2, v3], dtype=np.float32)

    return np.linalg.solve(matrix, target).astype(np.float32)
