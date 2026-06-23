import math
from typing import List, Optional, Tuple
from helpers.color import DEFAULT_COLOR, shade_tint
from triangle3d import Triangle3D

MAX_TRIANGLES_PER_SPRITE = 128


class Sprite3D:
    """A 3D sprite composed of triangles with transforms."""

    def __init__(self):
        """Initialize empty sprite at origin with default color."""
        self.triangles: List[Triangle3D] = []
        self.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.rotation_y = 0.0
        self.scale_factor = 1.0
        self.type_str = 'CUSTOM'
        self.active = True
        self.name = 'sprite'
        self._current_color = DEFAULT_COLOR

    def set_position(self, x: float, z: float, y: float = 0.0):
        """Set world position (x, z plane, optional y offset)."""
        self.position['x'] = x
        self.position['z'] = z
        self.position['y'] = y

    def set_rotation(self, r: float):
        """Set Y-axis rotation in radians."""
        self.rotation_y = r

    def set_scale(self, s: float):
        """Set uniform scale factor."""
        self.scale_factor = s

    def set_color(self, c: int):
        """Set default triangle color."""
        self._current_color = c

    def clear_triangles(self):
        """Remove all triangles."""
        self.triangles.clear()

    def get_triangle_count(self) -> int:
        """Return number of triangles."""
        return len(self.triangles)

    def add_triangle(self, x1: float, y1: float, z1: float,
                     x2: float, y2: float, z2: float,
                     x3: float, y3: float, z3: float,
                     color: Optional[int] = None):
        """Add a triangle with optional per-triangle color."""
        if len(self.triangles) >= MAX_TRIANGLES_PER_SPRITE:
            return
        c = color if color is not None else self._current_color
        self.triangles.append(Triangle3D(x1, y1, z1, x2, y2, z2, x3, y3, z3, c))

    def _transform_vertex(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Apply scale, rotation, and position transforms."""
        x *= self.scale_factor
        y *= self.scale_factor
        z *= self.scale_factor
        cos_a = math.cos(self.rotation_y)
        sin_a = math.sin(self.rotation_y)
        nx = x * cos_a - z * sin_a
        nz = x * sin_a + z * cos_a
        x = nx
        z = nz
        x += self.position['x']
        y += self.position.get('y', 0.0)
        z += self.position['z']
        return x, y, z

    def get_transformed_triangles(self) -> List[Triangle3D]:
        """Return triangles after applying sprite transforms."""
        result = []
        for t in self.triangles:
            v1 = self._transform_vertex(t.x1, t.y1, t.z1)
            v2 = self._transform_vertex(t.x2, t.y2, t.z2)
            v3 = self._transform_vertex(t.x3, t.y3, t.z3)
            result.append(Triangle3D(v1[0], v1[1], v1[2],
                                     v2[0], v2[1], v2[2],
                                     v3[0], v3[1], v3[2],
                                     t.color))
        return result

    def get_aabb(self) -> Tuple[float, float, float, float, float, float]:
        """Return axis-aligned bounding box (min_x, min_y, min_z, max_x, max_y, max_z)
        of all transformed triangles. Returns (0,0,0,0,0,0) if no triangles."""
        if not self.triangles:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        for t in self.triangles:
            for v in [(t.x1, t.y1, t.z1), (t.x2, t.y2, t.z2), (t.x3, t.y3, t.z3)]:
                tx, ty, tz = self._transform_vertex(*v)
                min_x = min(min_x, tx)
                min_y = min(min_y, ty)
                max_x = max(max_x, tx)
                max_y = max(max_y, ty)
                min_z = min(min_z, tz)
                max_z = max(max_z, tz)
        return (min_x, min_y, min_z, max_x, max_y, max_z)

    # Geometry helpers

    def _cube(self, x: float, y: float, z: float,
              width: float, height: float, depth: float,
              color: Optional[int] = None):
        """Generate cube triangles at position with given dimensions."""
        hw = width * 0.5
        hh = height * 0.5
        hd = depth * 0.5
        c = color if color is not None else self._current_color
        shade = lambda f: shade_tint(c, f)

        self.add_triangle(x - hw, y - hh, z + hd, x + hw, y - hh, z + hd, x + hw, y + hh, z + hd, shade(1.0))
        self.add_triangle(x - hw, y - hh, z + hd, x + hw, y + hh, z + hd, x - hw, y + hh, z + hd, shade(1.0))
        self.add_triangle(x + hw, y - hh, z - hd, x - hw, y - hh, z - hd, x - hw, y + hh, z - hd, shade(0.6))
        self.add_triangle(x + hw, y - hh, z - hd, x - hw, y + hh, z - hd, x + hw, y + hh, z - hd, shade(0.6))
        self.add_triangle(x + hw, y - hh, z + hd, x + hw, y - hh, z - hd, x + hw, y + hh, z - hd, shade(0.8))
        self.add_triangle(x + hw, y - hh, z + hd, x + hw, y + hh, z - hd, x + hw, y + hh, z + hd, shade(0.8))
        self.add_triangle(x - hw, y - hh, z - hd, x - hw, y - hh, z + hd, x - hw, y + hh, z + hd, shade(0.75))
        self.add_triangle(x - hw, y - hh, z - hd, x - hw, y + hh, z + hd, x - hw, y + hh, z - hd, shade(0.75))
        self.add_triangle(x - hw, y + hh, z + hd, x + hw, y + hh, z + hd, x + hw, y + hh, z - hd, shade(1.2))
        self.add_triangle(x - hw, y + hh, z + hd, x + hw, y + hh, z - hd, x - hw, y + hh, z - hd, shade(1.2))
        self.add_triangle(x - hw, y - hh, z - hd, x + hw, y - hh, z - hd, x + hw, y - hh, z + hd, shade(0.4))
        self.add_triangle(x - hw, y - hh, z - hd, x + hw, y - hh, z + hd, x - hw, y - hh, z + hd, shade(0.4))

    def _cylinder(self, x: float, y: float, z: float,
                  radius: float, height: float, segments: int = 6,
                  color: Optional[int] = None):
        """Generate cylinder triangles using stacked quads."""
        segments = min(segments, 12)
        hh = height * 0.5
        c = color if color is not None else self._current_color
        for i in range(segments):
            a1 = i * 2.0 * math.pi / segments
            a2 = (i + 1) * 2.0 * math.pi / segments
            x1 = x + radius * math.cos(a1)
            z1 = z + radius * math.sin(a1)
            x2 = x + radius * math.cos(a2)
            z2 = z + radius * math.sin(a2)
            self.add_triangle(x1, y - hh, z1, x2, y - hh, z2, x2, y + hh, z2, c)
            self.add_triangle(x1, y - hh, z1, x2, y + hh, z2, x1, y + hh, z1, c)

    def _sphere(self, x: float, y: float, z: float,
                radius: float, segments: int = 4,
                color: Optional[int] = None):
        """Generate sphere triangles using lat/lon segments."""
        segments = min(segments, 8)
        half_seg = segments // 2
        c = color if color is not None else self._current_color
        for lat in range(half_seg):
            t1 = lat * math.pi / half_seg
            t2 = (lat + 1) * math.pi / half_seg
            for lon in range(segments):
                p1 = lon * 2.0 * math.pi / segments
                p2 = (lon + 1) * 2.0 * math.pi / segments
                x1 = x + radius * math.sin(t1) * math.cos(p1)
                y1 = y + radius * math.cos(t1)
                z1 = z + radius * math.sin(t1) * math.sin(p1)
                x2 = x + radius * math.sin(t1) * math.cos(p2)
                y2 = y + radius * math.cos(t1)
                z2 = z + radius * math.sin(t1) * math.sin(p2)
                x3 = x + radius * math.sin(t2) * math.cos(p1)
                y3 = y + radius * math.cos(t2)
                z3 = z + radius * math.sin(t2) * math.sin(p1)
                x4 = x + radius * math.sin(t2) * math.cos(p2)
                y4 = y + radius * math.cos(t2)
                z4 = z + radius * math.sin(t2) * math.sin(p2)
                if lat > 0:
                    self.add_triangle(x1, y1, z1, x2, y2, z2, x3, y3, z3, c)
                if lat < half_seg - 1:
                    self.add_triangle(x2, y2, z2, x4, y4, z4, x3, y3, z3, c)

    def _triangular_prism(self, x: float, y: float, z: float,
                          width: float, height: float, depth: float,
                          color: Optional[int] = None):
        """Generate triangular prism (roof shape) triangles."""
        hw = width * 0.5
        hh = height * 0.5
        hd = depth * 0.5
        c = color if color is not None else self._current_color
        self.add_triangle(x - hw, y - hh, z + hd, x + hw, y - hh, z + hd, x, y + hh, z + hd, c)
        self.add_triangle(x + hw, y - hh, z - hd, x - hw, y - hh, z - hd, x, y + hh, z - hd, c)
        self.add_triangle(x - hw, y - hh, z - hd, x + hw, y - hh, z - hd, x + hw, y - hh, z + hd, c)
        self.add_triangle(x - hw, y - hh, z - hd, x + hw, y - hh, z + hd, x - hw, y - hh, z + hd, c)
        self.add_triangle(x - hw, y - hh, z + hd, x, y + hh, z + hd, x, y + hh, z - hd, c)
        self.add_triangle(x - hw, y - hh, z + hd, x, y + hh, z - hd, x - hw, y - hh, z - hd, c)
        self.add_triangle(x, y + hh, z + hd, x + hw, y - hh, z + hd, x + hw, y - hh, z - hd, c)
        self.add_triangle(x, y + hh, z + hd, x + hw, y - hh, z - hd, x, y + hh, z - hd, c)

    # Preset generators

    def create_humanoid(self, height: float = 1.8):
        """Generate a blocky humanoid character."""
        self.clear_triangles()
        self.type_str = 'HUMANOID'
        hr = height * 0.12
        tw = height * 0.20
        th = height * 0.35
        lh = height * 0.45
        al = height * 0.25
        self._sphere(0, height - hr, 0, hr, 4, 0xffcc99)
        self._cube(0, lh + th / 2, 0, tw, th, tw * 0.8, 0x4466aa)
        aw = tw * 0.35
        ay = lh + th - al / 2
        self._cube(-tw * 0.8, ay, 0, aw, al, aw, 0x4466aa)
        self._cube(tw * 0.8, ay, 0, aw, al, aw, 0x4466aa)
        lw = tw * 0.45
        self._cube(-lw * 0.7, lh / 2, 0, lw, lh, lw, 0x334488)
        self._cube(lw * 0.7, lh / 2, 0, lw, lh, lw, 0x334488)

    def create_tree(self, height: float = 2.0):
        """Generate a blocky tree."""
        self.clear_triangles()
        self.type_str = 'TREE'
        trw = height * 0.18
        trh = height * 0.4
        crw = height * 0.65
        crh = height * 0.6
        self._cube(0, trh / 2, 0, trw, trh, trw, 0x5c3d11)
        self._cube(0, trh + crh / 2, 0, crw, crh, crw, 0x2d6e2d)

    def create_house(self, width: float = 2.0, height: float = 2.5):
        """Generate a house shape with triangular roof."""
        self.clear_triangles()
        self.type_str = 'HOUSE'
        wh = height * 0.7
        rh = height * 0.3
        hw = width * 1.3
        hd = width * 1.1
        self._cube(0, wh / 2, 0, hw, wh, hd, 0xd4b896)
        self._triangular_prism(0, wh + rh / 2, 0, hw, rh, hd, 0x8b2020)

    def create_pillar(self, height: float = 3.0, radius: float = 0.3):
        """Generate a cylindrical pillar."""
        self.clear_triangles()
        self.type_str = 'PILLAR'
        pr = radius * 1.5
        self._cylinder(0, height / 2, 0, pr, height, 6, 0xccbbaa)
        self._cylinder(0, pr * 0.4, 0, pr * 1.4, pr * 0.8, 4, 0xbbaa99)
        self._cylinder(0, height - pr * 0.4, 0, pr * 1.4, pr * 0.8, 4, 0xbbaa99)
