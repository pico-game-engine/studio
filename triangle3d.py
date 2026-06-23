from typing import Tuple
from helpers.color import DEFAULT_COLOR


class Triangle3D:
    """A single 3D triangle with position and color."""
    __slots__ = ('x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 'color')

    def __init__(self, x1: float, y1: float, z1: float,
                 x2: float, y2: float, z2: float,
                 x3: float, y3: float, z3: float,
                 color: int = DEFAULT_COLOR):
        """Store three vertices and an optional color."""
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1
        self.x2 = x2
        self.y2 = y2
        self.z2 = z2
        self.x3 = x3
        self.y3 = y3
        self.z3 = z3
        self.color = color

    def get_center(self) -> Tuple[float, float, float]:
        """Return the centroid of the triangle."""
        cx = (self.x1 + self.x2 + self.x3) / 3.0
        cy = (self.y1 + self.y2 + self.y3) / 3.0
        cz = (self.z1 + self.z2 + self.z3) / 3.0
        return cx, cy, cz

    def get_normal(self) -> Tuple[float, float, float]:
        """Return the surface normal vector."""
        ax = self.x2 - self.x1
        ay = self.y2 - self.y1
        az = self.z2 - self.z1
        bx = self.x3 - self.x1
        by = self.y3 - self.y1
        bz = self.z3 - self.z1
        return (ay * bz - az * by,
                az * bx - ax * bz,
                ax * by - ay * bx)
