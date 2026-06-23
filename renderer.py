import math
import time
from typing import List, Optional, Tuple
import tkinter as tk
from helpers.color import hex_to_rgb
from sprite3d import Sprite3D


class Renderer:
    """Projects and draws 3D triangles onto a tkinter canvas."""

    def __init__(self, canvas: tk.Canvas):
        """Initialize renderer with target canvas and default settings."""
        self.canvas = canvas
        self.sprites: List[Sprite3D] = []
        self.camera = {
            'azimuth': 0.0,
            'elevation': 3.0 * math.pi / 180.0,
            'zoom': 8.0,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'pan_z': 0.0,
            'roll': 0.0,
        }
        self.opts = {
            'wireframe': True,
            'solid': True,
            'backface': False,
            'grid': True,
            'axes': True,
            'normals': False,
            'color': True,
        }
        self.lighting = {'ambient': 0.3, 'diffuse': 0.7}
        self.fov = 60.0
        self._fps = 0
        self._frame_count = 0
        self._fps_time = 0.0
        self.mouse_down = False
        self.mouse_x = 0
        self.mouse_y = 0
        self._anim_id = None

    def get_camera_pos(self):
        """Return camera world position from azimuth/elevation/zoom."""
        az = self.camera['azimuth']
        el = self.camera['elevation'] + self.camera.get('roll', 0.0)
        zoom = self.camera['zoom']
        px = self.camera['pan_x']
        py = self.camera['pan_y']
        pz = self.camera.get('pan_z', 0.0)
        return (zoom * math.cos(el) * math.sin(az) + px,
                zoom * math.sin(el) + py,
                zoom * math.cos(el) * math.cos(az) + pz)

    def project(self, wx: float, wy: float, wz: float) -> Optional[Tuple[float, float, float]]:
        """Project 3D world point to 2D screen coordinates. Returns None if behind camera."""
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 1 or H < 1:
            return None
        az = self.camera['azimuth']
        el = self.camera['elevation'] + self.camera.get('roll', 0.0)
        cos_a = math.cos(az)
        sin_a = math.sin(az)
        cos_e = math.cos(el)
        sin_e = math.sin(el)
        cx = self.camera['zoom'] * cos_e * sin_a + self.camera['pan_x']
        cy = self.camera['zoom'] * sin_e + self.camera.get('pan_y', 0.0)
        cz = self.camera['zoom'] * cos_e * cos_a + self.camera.get('pan_z', 0.0)

        dx = wx - cx
        dy = wy - cy
        dz = wz - cz

        rx = cos_a * dx - sin_a * dz
        rz = sin_a * dx + cos_a * dz
        dx = rx
        dz = rz

        ry = cos_e * dy - sin_e * dz
        rz2 = sin_e * dy + cos_e * dz
        dy = ry
        dz = rz2

        if dz >= -0.01:
            return None

        fov_rad = self.fov * math.pi / 360.0
        f = (W * 0.5) / math.tan(fov_rad)
        sx = W / 2.0 + (dx / (-dz)) * f
        sy = H / 2.0 - (dy / (-dz)) * f
        return (sx, sy, dz)

    def render(self):
        """Render all sprites: clear canvas, draw grid/axes, sort and draw triangles."""
        try:
            self.canvas.delete('all')
        except tk.TclError:
            return
        c = self.canvas
        try:
            W = c.winfo_width()
            H = c.winfo_height()
        except tk.TclError:
            return
        if W < 2 or H < 2:
            return

        c.create_rectangle(0, 0, W, H, fill='#070d0a', outline='')

        cam = self.get_camera_pos()
        opts = self.opts
        light = self.lighting

        if opts['grid']:
            for i in range(-10, 11):
                a = self.project(i, 0, -10)
                b = self.project(i, 0, 10)
                c_pt = self.project(-10, 0, i)
                d = self.project(10, 0, i)
                if a and b:
                    c.create_line(a[0], a[1], b[0], b[1], fill='#001133', width=1)
                if c_pt and d:
                    c.create_line(c_pt[0], c_pt[1], d[0], d[1], fill='#001133', width=1)
            ox = self.project(0, 0, -10)
            ox2 = self.project(0, 0, 10)
            oz = self.project(-10, 0, 0)
            oz2 = self.project(10, 0, 0)
            if ox and ox2:
                c.create_line(ox[0], ox[1], ox2[0], ox2[1], fill='#003366', width=1)
            if oz and oz2:
                c.create_line(oz[0], oz[1], oz2[0], oz2[1], fill='#003366', width=1)

        if opts['axes']:
            o = self.project(0, 0, 0)
            ax = self.project(1, 0, 0)
            ay = self.project(0, 1, 0)
            az2 = self.project(0, 0, 1)
            if o and ax:
                c.create_line(o[0], o[1], ax[0], ax[1], fill='#ff4455', width=2)
            if o and ay:
                c.create_line(o[0], o[1], ay[0], ay[1], fill='#4488ff', width=2)
            if o and az2:
                c.create_line(o[0], o[1], az2[0], az2[1], fill='#44aaff', width=2)

        all_tris = []
        for sprite in self.sprites:
            if not sprite.active:
                continue
            for t in sprite.get_transformed_triangles():
                cx, cy, cz = t.get_center()
                dist = ((cx - cam[0]) ** 2 +
                        (cy - cam[1]) ** 2 +
                        (cz - cam[2]) ** 2)
                all_tris.append((t, dist))
        all_tris.sort(key=lambda x: x[1], reverse=True)

        lx, ly, lz = 0.5, 1.0, 0.3
        llen = math.sqrt(lx * lx + ly * ly + lz * lz)
        vis_count = 0

        for t, _ in all_tris:
            p1 = self.project(t.x1, t.y1, t.z1)
            p2 = self.project(t.x2, t.y2, t.z2)
            p3 = self.project(t.x3, t.y3, t.z3)
            if not p1 or not p2 or not p3:
                continue

            nx = (p2[0] - p1[0])
            ny = (p2[1] - p1[1])
            mx = (p3[0] - p1[0])
            my = (p3[1] - p1[1])
            cross = nx * my - ny * mx
            is_front = cross < 0
            if not is_front and not opts['backface']:
                continue

            vis_count += 1

            norm = t.get_normal()
            nlen = math.sqrt(norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2)
            lit = light['ambient']
            if nlen > 0.001:
                ndot = (norm[0] * lx + norm[1] * ly + norm[2] * lz) / (nlen * llen)
                lit += light['diffuse'] * max(0.0, ndot if is_front else -ndot)
            lit = min(1.0, lit)

            pts = [p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]]

            if opts['solid']:
                if opts['color']:
                    r, g, b = hex_to_rgb(t.color)
                    r = int(r * lit)
                    g = int(g * lit)
                    b = int(b * lit)
                    fill = f'#{r:02x}{g:02x}{b:02x}'
                else:
                    v = int(lit * 200)
                    g2 = int(lit * 255)
                    if is_front:
                        fill = f'#{int(v*0.3):02x}{int(v*0.6):02x}{g2:02x}'
                    else:
                        fill = f'#{int(v*0.6):02x}{int(v*0.3):02x}{int(v*0.3):02x}'
                c.create_polygon(pts, fill=fill, outline='', width=0)

            if opts['wireframe']:
                outline = '#001133' if is_front else '#331015'
                c.create_polygon(pts, fill='', outline=outline, width=1)

            if opts['normals']:
                cx, cy, cz = t.get_center()
                nl = math.sqrt(norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2)
                if nl > 0:
                    cp = self.project(cx, cy, cz)
                    ep = self.project(cx + norm[0] / nl * 0.3,
                                      cy + norm[1] / nl * 0.3,
                                      cz + norm[2] / nl * 0.3)
                    if cp and ep:
                        c.create_line(cp[0], cp[1], ep[0], ep[1], fill='#ffcc00', width=1)

        total_tris = len(all_tris)
        self._frame_count += 1
        t_now = time.time() * 1000
        if self._fps_time == 0:
            self._fps_time = t_now
        if t_now - self._fps_time >= 500:
            self._fps = int(self._frame_count * 1000.0 / (t_now - self._fps_time))
            self._frame_count = 0
            self._fps_time = t_now

        return total_tris, vis_count, len(self.sprites), self._fps