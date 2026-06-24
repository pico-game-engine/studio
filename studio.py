"""Pico Game Engine Studio"""

import math
import tkinter as tk
from typing import List, Optional
import customtkinter as ctk

from helpers.color import hex_to_tk_color
from sprite3d import Sprite3D
from triangle3d import Triangle3D
from renderer import Renderer
from views.code_view import CodeView
from views.creator_view import CreatorView
from views.library_view import LibraryView
from views.settings_view import SettingsView
from views.export_view import ExportView
from views.property_view import PropertyEditor


ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')


class Studio(ctk.CTk):
    """Main application window for Pico Game Engine Studio."""

    def __init__(self):
        """Initialize the app window, UI, renderer, and load default preset."""
        super().__init__()
        self.title('Pico Game Engine Studio')
        self.geometry('1400x850')
        self.minsize(1000, 600)

        self.sprites: List[Sprite3D] = []
        self.renderer: Optional[Renderer] = None
        self.active_sprite: Optional[Sprite3D] = None
        self.console_logs: List[str] = []

        self.creator_color = 0x4466aa
        self.creator_colors = [
            0xffcc99, 0x4466aa, 0x334488, 0x2d6e2d, 0x5c3d11,
            0xd4b896, 0x8b2020, 0xccbbaa, 0xaa8855, 0x00ff88,
            0xff4455, 0x44aaff, 0xffcc00, 0x666666, 0x111111
        ]

        self.palette_mode: Optional[str] = None

        self._build_ui()
        self._bind_events()
        self._init_renderer()

    def _build_ui(self):
        """Build the main layout: header, viewport, panel, camera bar."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        header = ctk.CTkFrame(self, height=48, corner_radius=0, border_width=0)
        header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_font = ctk.CTkFont(family='Orbitron', size=16, weight='bold')
        title = ctk.CTkLabel(header, text='PICO GAME ENGINE STUDIO', font=title_font,
                             text_color='#4488ff')
        title.grid(row=0, column=0, padx=20, pady=8, sticky='w')

        self.status_fps = ctk.CTkLabel(header, text='-- FPS', font=('Share Tech Mono', 11),
                                        text_color='#5a6a88')
        self.status_fps.grid(row=0, column=1, padx=8, pady=8, sticky='e')
        self.status_tris = ctk.CTkLabel(header, text='0 TRIS', font=('Share Tech Mono', 11),
                                         text_color='#5a6a88')
        self.status_tris.grid(row=0, column=2, padx=8, pady=8, sticky='e')
        self.status_objs = ctk.CTkLabel(header, text='0 OBJS', font=('Share Tech Mono', 11),
                                         text_color='#5a6a88')
        self.status_objs.grid(row=0, column=3, padx=20, pady=8, sticky='e')

        main_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color='#070d0a')
        main_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_rowconfigure(0, weight=1)

        viewport_frame = ctk.CTkFrame(main_frame, corner_radius=0)
        viewport_frame.grid(row=0, column=0, sticky='nsew')
        viewport_frame.grid_rowconfigure(1, weight=1)
        viewport_frame.grid_columnconfigure(0, weight=1)

        viewport_header = ctk.CTkFrame(viewport_frame, height=28, corner_radius=0, border_width=0)
        viewport_header.grid(row=0, column=0, sticky='ew')
        viewport_header.grid_columnconfigure(0, weight=1)

        self.cam_info = ctk.CTkLabel(viewport_header, text='azimuth 0 / elevation 3 / zoom 8.0',
                                      font=('Share Tech Mono', 10), text_color='#5a6a88')
        self.cam_info.grid(row=0, column=0, padx=12, pady=4, sticky='w')

        self.render_mode_label = ctk.CTkLabel(viewport_header, text='WIREFRAME + SOLID',
                                               font=('Share Tech Mono', 10), text_color='#4488ff')
        self.render_mode_label.grid(row=0, column=1, padx=12, pady=4, sticky='e')

        self.canvas_3d = tk.Canvas(viewport_frame, bg='#070d0a', highlightthickness=0)
        self.canvas_3d.grid(row=1, column=0, sticky='nsew')

        panel_frame = ctk.CTkFrame(main_frame, width=440, corner_radius=0, border_width=0)
        panel_frame.grid(row=0, column=1, sticky='nsew')
        panel_frame.grid_propagate(False)
        panel_frame.grid_rowconfigure(1, weight=1)
        panel_frame.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(panel_frame, corner_radius=0, border_width=0)
        self.tab_view.grid(row=0, column=0, rowspan=2, sticky='nsew')

        self.tab_view.add('Code')
        self.tab_view.add('Creator')
        self.tab_view.add('Library')
        self.tab_view.add('Export')
        self.tab_view.add('Settings')

        cam_bar = ctk.CTkFrame(self, height=40, corner_radius=0, border_width=0)
        cam_bar.grid(row=2, column=0, columnspan=2, sticky='ew')
        self._build_camera_controls(cam_bar)

        CodeView(self, self.tab_view.tab('Code'))
        self.creator_view = CreatorView(self, self.tab_view.tab('Creator'))
        LibraryView(self, self.tab_view.tab('Library'))
        ExportView(self, self.tab_view.tab('Export'))
        SettingsView(self, self.tab_view.tab('Settings'))

    def _build_camera_controls(self, parent):
        """Build camera slider controls (azimuth, elevation, zoom, pan)."""
        labels_def = [
            ('ROTATION', 'ctrl_azimuth', -180, 180, 0),
            ('ELEVATION', 'ctrl_elevation', -90, 90, 3),
            ('ROLL', 'ctrl_roll', -180, 180, 0),
            ('ZOOM', 'ctrl_zoom', 1, 30, 8),
            ('PAN X', 'ctrl_panx', -50, 50, 0),
        ]

        for i, (label, attr, min_v, max_v, default) in enumerate(labels_def):
            f = ctk.CTkFrame(parent, corner_radius=0, fg_color='transparent')
            f.grid(row=0, column=i, padx=4, pady=2, sticky='w')
            ctk.CTkLabel(f, text=label, font=('Share Tech Mono', 9),
                          text_color='#5a6a88', width=60).pack(side='left')
            slider = ctk.CTkSlider(f, from_=min_v, to=max_v, width=80,
                                    command=lambda v, a=attr: self._on_cam_slider(a, v))
            slider.set(default)
            slider.pack(side='left', padx=2)
            val_label = ctk.CTkLabel(f, text=str(default), font=('Share Tech Mono', 9),
                                      text_color='#4488ff', width=30)
            val_label.pack(side='left')
            setattr(self, attr, slider)
            setattr(self, f'val_{attr}', val_label)

        self.cam_reset_btn = ctk.CTkButton(parent, text='RESET', width=60, height=24,
                                            font=('Share Tech Mono', 10),
                                            command=self._reset_camera)
        self.cam_reset_btn.grid(row=0, column=len(labels_def), padx=4, pady=2, sticky='w')

        hint = ctk.CTkLabel(parent, text='DRAG orbit | CTRL+DRAG pan | SCROLL zoom | G grid | W wire',
                             font=('Share Tech Mono', 9), text_color='#5a6a88')
        hint.grid(row=0, column=len(labels_def) + 1, padx=8, pady=2, sticky='e')
        parent.grid_columnconfigure(len(labels_def) + 1, weight=1)

    def _bind_events(self):
        """Bind mouse and keyboard event handlers."""
        self.canvas_3d.bind('<Button-1>', self._canvas_mouse_down)
        self.canvas_3d.bind('<B1-Motion>', self._canvas_orbit_drag)
        self.canvas_3d.bind('<Control-B1-Motion>', self._canvas_pan_drag)
        self.canvas_3d.bind('<Command-B1-Motion>', self._canvas_pan_drag)
        self.canvas_3d.bind('<ButtonRelease-1>', self._canvas_mouse_up)
        self.canvas_3d.bind('<Double-Button-1>', self._canvas_double_click)
        self.canvas_3d.bind('<MouseWheel>', self._canvas_wheel)
        # Linux scroll wheel support (Button-4 = up, Button-5 = down)
        self.canvas_3d.bind('<Button-4>', self._canvas_wheel_linux)
        self.canvas_3d.bind('<Button-5>', self._canvas_wheel_linux)
        self.canvas_3d.bind('<Enter>', lambda e: setattr(self, '_mouse_over_canvas', True))
        self.canvas_3d.bind('<Leave>', lambda e: setattr(self, '_mouse_over_canvas', False))

        self.bind('<Control-Return>', lambda e: self._run_code())
        self.bind('<Control-r>', lambda e: self._run_code())
        self.bind('<Key>', self._key_press)

        self.code_editor.bind('<Control-Return>', lambda e: self._run_code())

    def _key_press(self, e):
        """Handle keyboard shortcuts (G, W, R, Escape)."""
        if e.widget in (self.code_editor, self.export_output):
            return
        if e.char == 'g' or e.char == 'G':
            var = self.check_vars.get('grid')
            if var:
                var.set(not var.get())
                self._update_opts()
        elif e.char == 'w' or e.char == 'W':
            var = self.check_vars.get('wireframe')
            if var:
                var.set(not var.get())
                self._update_opts()
        elif e.char == 'r' or e.char == 'R':
            self._reset_camera()
        elif e.keysym == 'Escape':
            if self.palette_mode:
                self._cancel_palette()

    def _init_renderer(self):
        """Create renderer and start render loop."""
        self.renderer = Renderer(self.canvas_3d)
        self.renderer.sprites = self.sprites
        self._last_stats = (0, 0, 0, 0)
        self._render_loop()

    def _render_loop(self):
        """Continuously render frames at ~60fps."""
        try:
            if not self.winfo_exists():
                return
            if self.renderer:
                stats = self.renderer.render()
                if stats:
                    self._last_stats = stats
                    self._update_stats(*stats)
            self.after(16, self._render_loop)
        except tk.TclError:
            pass

    def _update_stats(self, total_tris, vis_count, obj_count, fps):
        """Update status bar and stats labels."""
        self.status_tris.configure(text=f'{total_tris} TRIS')
        self.status_fps.configure(text=f'{fps} FPS')
        self.status_objs.configure(text=f'{obj_count} OBJS')
        if 'tris' in self.stat_labels:
            self.stat_labels['tris'].configure(text=str(total_tris))
        if 'vis' in self.stat_labels:
            self.stat_labels['vis'].configure(text=str(vis_count))
        if 'objs' in self.stat_labels:
            self.stat_labels['objs'].configure(text=str(obj_count))
        if 'fps' in self.stat_labels:
            self.stat_labels['fps'].configure(text=str(fps) if fps else '--')

    def _on_cam_slider(self, attr, value):
        """Handle camera slider changes."""
        mapping = {
            'ctrl_azimuth': 'azimuth',
            'ctrl_elevation': 'elevation',
            'ctrl_roll': 'roll',
            'ctrl_zoom': 'zoom',
            'ctrl_panx': 'pan_x',
        }
        if attr in mapping:
            key = mapping[attr]
            if key in ('azimuth', 'elevation', 'roll'):
                self.renderer.camera[key] = value * math.pi / 180.0
            else:
                self.renderer.camera[key] = value

        val_label = getattr(self, f'val_{attr}', None)
        if val_label:
            if attr in ('ctrl_azimuth', 'ctrl_elevation', 'ctrl_roll'):
                val_label.configure(text=f'{int(value)}')
            else:
                val_label.configure(text=str(int(value)))

        self._update_cam_info()

    def _update_cam_info(self):
        """Update camera info label and render mode label."""
        cam = self.renderer.camera
        az = cam['azimuth'] * 180 / math.pi
        el = cam['elevation'] * 180 / math.pi
        zm = cam['zoom']
        self.cam_info.configure(
            text=f'azimuth {az:.0f} / elevation {el:.0f} / zoom {zm:.1f}')

        w = self.check_vars.get('wireframe', ctk.BooleanVar()).get() if hasattr(self, 'check_vars') else True
        s = self.check_vars.get('solid', ctk.BooleanVar()).get() if hasattr(self, 'check_vars') else True
        if w and s:
            self.render_mode_label.configure(text='WIREFRAME + SOLID')
        elif w:
            self.render_mode_label.configure(text='WIREFRAME')
        elif s:
            self.render_mode_label.configure(text='SOLID')
        else:
            self.render_mode_label.configure(text='NONE')

    def _reset_camera(self):
        """Reset camera to default position."""
        self.renderer.camera = {
            'azimuth': 0.0,
            'elevation': 3.0 * math.pi / 180.0,
            'zoom': 8.0,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'pan_z': 0.0,
            'roll': 0.0,
        }
        for attr, val in [('ctrl_azimuth', 0), ('ctrl_elevation', 3),
                          ('ctrl_roll', 0),
                          ('ctrl_zoom', 8), ('ctrl_panx', 0)]:
            slider = getattr(self, attr, None)
            if slider:
                slider.set(val)
            val_label = getattr(self, f'val_{attr}', None)
            if val_label:
                if attr in ('ctrl_azimuth', 'ctrl_elevation'):
                    val_label.configure(text=f'{val}')
                else:
                    val_label.configure(text=str(val))
        self._update_cam_info()

    def _canvas_mouse_down(self, e):
        """Start orbit drag on canvas, or place palette object."""
        if self.palette_mode:
            W = self.canvas_3d.winfo_width()
            H = self.canvas_3d.winfo_height()
            if W > 1 and H > 1:
                cam = self.renderer.camera
                az = cam['azimuth']
                el = cam['elevation'] + cam.get('roll', 0.0)
                zoom = cam['zoom']
                cos_a = math.cos(az)
                sin_a = math.sin(az)
                cos_e = math.cos(el)
                sin_e = math.sin(el)

                # Camera world position
                cx = zoom * cos_e * sin_a + cam['pan_x']
                cy = zoom * sin_e + cam.get('pan_y', 0.0)
                cz = zoom * cos_e * cos_a + cam.get('pan_z', 0.0)

                # Screen to camera ray direction
                fov_rad = self.renderer.fov * math.pi / 360.0
                f = (W * 0.5) / math.tan(fov_rad)
                dir_x = (e.x - W / 2) / f
                dir_y = -(e.y - H / 2) / f
                dir_z = -1.0

                # Ground plane hit
                denom = cos_e * dir_y - sin_e
                if abs(denom) > 1e-8:
                    t = -cy / denom
                    if t > 0:
                        # Camera offset at t
                        dcx = dir_x * t
                        dcy = dir_y * t
                        dcz = dir_z * t

                        # Inverse elevation
                        dy_w = cos_e * dcy + sin_e * dcz
                        dz_w = -sin_e * dcy + cos_e * dcz

                        # Inverse azimuth
                        dx_w = cos_a * dcx + sin_a * dz_w
                        dz_final = -sin_a * dcx + cos_a * dz_w

                        world_x = cx + dx_w
                        world_z = cz + dz_final
                        self._place_palette_object(world_x, world_z)
            return
        self._mouse_down = True
        self._mouse_x = e.x
        self._mouse_y = e.y

    def _canvas_orbit_drag(self, e):
        """Orbit camera on mouse drag."""
        if not getattr(self, '_mouse_down', False):
            return
        dx = e.x - self._mouse_x
        dy = e.y - self._mouse_y
        cam = self.renderer.camera
        cam['azimuth'] += dx * 0.01
        cam['elevation'] = max(-math.pi / 2, min(math.pi / 2, cam['elevation'] - dy * 0.01))
        self._mouse_x = e.x
        self._mouse_y = e.y
        az_deg = int(cam['azimuth'] * 180 / math.pi)
        el_deg = int(cam['elevation'] * 180 / math.pi)
        self.ctrl_azimuth.set(az_deg)
        self.ctrl_elevation.set(el_deg)
        self.val_ctrl_azimuth.configure(text=f'{az_deg}')
        self.val_ctrl_elevation.configure(text=f'{el_deg}')
        self._update_cam_info()

    def _compute_ground_point(self, sx, sy):
        """Return (x, y, z) pivot from screen point. Tries object hit, then ground, then fallback."""
        # Try hitting a sprite first
        sprite = self._hit_test_sprites(sx, sy)
        if sprite:
            aabb = sprite.get_aabb()
            return ((aabb[0] + aabb[3]) / 2,
                    (aabb[1] + aabb[4]) / 2,
                    (aabb[2] + aabb[5]) / 2)
        # Try ground plane intersection
        ray = self._compute_ray(sx, sy)
        if ray:
            origin, direction = ray
            if abs(direction[1]) >= 1e-8:
                t = -origin[1] / direction[1]
                if t > 0:
                    return (origin[0] + direction[0] * t, 0.0,
                            origin[2] + direction[2] * t)

        cam = self.renderer.camera
        return (cam.get('pan_x', 0.0), 0.0, cam.get('pan_z', 0.0))

    def _canvas_pan_drag(self, e):
        """Pan the camera (translate the look-at target) on Ctrl+drag."""
        if not getattr(self, '_mouse_down', False):
            return
        dx = e.x - self._mouse_x
        dy = e.y - self._mouse_y

        cam = self.renderer.camera
        W = self.canvas_3d.winfo_width()
        H = self.canvas_3d.winfo_height()
        if W < 2 or H < 2:
            self._mouse_x = e.x
            self._mouse_y = e.y
            return

        az = cam['azimuth']
        el = cam['elevation'] + cam.get('roll', 0.0)
        zoom = cam['zoom']
        cos_a = math.cos(az)
        sin_a = math.sin(az)
        cos_e = math.cos(el)
        sin_e = math.sin(el)

        # Camera right/up in world space
        right = (cos_a, 0.0, -sin_a)
        up = (-sin_a * sin_e, cos_e, -cos_a * sin_e)

        # Pixels to world units
        fov_rad = self.renderer.fov * math.pi / 360.0
        f = (W * 0.5) / math.tan(fov_rad)
        world_per_px = zoom / f

        move_h = dx * world_per_px
        move_v = dy * world_per_px

        cam['pan_x'] = cam['pan_x'] - right[0] * move_h + up[0] * move_v
        cam['pan_y'] = cam.get('pan_y', 0.0) - right[1] * move_h + up[1] * move_v
        cam['pan_z'] = cam.get('pan_z', 0.0) - right[2] * move_h + up[2] * move_v

        self._mouse_x = e.x
        self._mouse_y = e.y

        panx_slider = getattr(self, 'ctrl_panx', None)
        if panx_slider:
            panx_slider.set(cam['pan_x'])
            val_label = getattr(self, 'val_ctrl_panx', None)
            if val_label:
                val_label.configure(text=str(int(cam['pan_x'])))

        self._update_cam_info()

    def _canvas_mouse_up(self, e):
        """End drag."""
        self._mouse_down = False

    def _canvas_wheel(self, e):
        """Handle scroll wheel zoom (macOS/Windows)."""
        cam = self.renderer.camera
        delta = e.delta
        cam['zoom'] = max(1, min(30, cam['zoom'] + delta * 0.05))
        self.ctrl_zoom.set(int(cam['zoom']))
        self.val_ctrl_zoom.configure(text=str(int(cam['zoom'])))
        self._update_cam_info()

    def _canvas_wheel_linux(self, e):
        """Handle scroll wheel zoom on Linux (Button-4/Button-5)."""
        cam = self.renderer.camera
        # Button-4 = scroll up (zoom in), Button-5 = scroll down (zoom out)
        delta = 1.0 if e.num == 4 else -1.0
        cam['zoom'] = max(1, min(30, cam['zoom'] + delta * 0.5))
        self.ctrl_zoom.set(int(cam['zoom']))
        self.val_ctrl_zoom.configure(text=str(int(cam['zoom'])))
        self._update_cam_info()

    def _compute_ray(self, sx, sy):
        """Return (ray_origin, ray_dir) in world space from a screen point."""
        W = self.canvas_3d.winfo_width()
        H = self.canvas_3d.winfo_height()
        if W < 2 or H < 2:
            return None
        cam = self.renderer.camera
        az = cam['azimuth']
        el = cam['elevation'] + cam.get('roll', 0.0)
        zoom = cam['zoom']
        cos_a = math.cos(az)
        sin_a = math.sin(az)
        cos_e = math.cos(el)
        sin_e = math.sin(el)

        cx = zoom * cos_e * sin_a + cam['pan_x']
        cy = zoom * sin_e + cam.get('pan_y', 0.0)
        cz = zoom * cos_e * cos_a + cam.get('pan_z', 0.0)

        fov_rad = self.renderer.fov * math.pi / 360.0
        f = (W * 0.5) / math.tan(fov_rad)
        dir_x = (sx - W / 2) / f
        dir_y = -(sy - H / 2) / f
        dir_z = -1.0

        # Inverse elevation then azimuth
        dy_w = cos_e * dir_y + sin_e * dir_z
        dz_w = -sin_e * dir_y + cos_e * dir_z
        dx_w = cos_a * dir_x + sin_a * dz_w
        dz_final = -sin_a * dir_x + cos_a * dz_w

        length = math.sqrt(dx_w * dx_w + dy_w * dy_w + dz_final * dz_final)
        if length < 1e-10:
            return None
        return ((cx, cy, cz), (dx_w / length, dy_w / length, dz_final / length))

    def _ray_aabb_intersect(self, origin, direction, aabb):
        """Ray-AABB intersection using slab method. Returns t or None."""
        min_x, min_y, min_z, max_x, max_y, max_z = aabb
        ox, oy, oz = origin
        dx, dy, dz = direction

        t_min = float('-inf')
        t_max = float('inf')

        for i in range(3):
            o = [ox, oy, oz][i]
            d = [dx, dy, dz][i]
            a = [min_x, min_y, min_z][i]
            b = [max_x, max_y, max_z][i]

            if abs(d) < 1e-10:
                if o < a or o > b:
                    return None
            else:
                t1 = (a - o) / d
                t2 = (b - o) / d
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max + 1e-10:
                    return None

        return t_min if t_min > 0 else None

    def _hit_test_sprites(self, sx, sy):
        """Return the closest sprite hit by a ray from screen point, or None."""
        ray = self._compute_ray(sx, sy)
        if not ray:
            return None
        origin, direction = ray
        closest = None
        closest_t = float('inf')
        for sprite in self.sprites:
            if not sprite.active or not sprite.triangles:
                continue
            aabb = sprite.get_aabb()
            t = self._ray_aabb_intersect(origin, direction, aabb)
            if t is not None and 0 < t < closest_t:
                closest = sprite
                closest_t = t
        return closest

    def _canvas_double_click(self, e):
        """Double-click to select a sprite and open its property editor."""
        if self.palette_mode:
            return
        sprite = self._hit_test_sprites(e.x, e.y)
        if sprite:
            self._open_property_editor(sprite)

    def _open_property_editor(self, sprite):
        """Open the property editor window for the given sprite."""
        if hasattr(self, '_prop_editor') and self._prop_editor is not None:
            try:
                self._prop_editor.destroy()
            except Exception:
                pass
        self._prop_editor = PropertyEditor(self, sprite, on_update=self._on_property_update)

    def _on_property_update(self, sprite):
        """Called after property editor changes a sprite."""
        self._sync_code_from_sprites()

    def _update_opts(self, *args):
        """Sync UI controls to renderer options."""
        if not self.renderer:
            return
        for key, var in self.check_vars.items():
            self.renderer.opts[key] = var.get()

        self.renderer.lighting['ambient'] = self.light_ambient.get() / 100.0
        self.renderer.lighting['diffuse'] = self.light_diffuse.get() / 100.0
        self.lbl_ambient.configure(text=f'{self.renderer.lighting["ambient"]:.2f}')
        self.lbl_diffuse.configure(text=f'{self.renderer.lighting["diffuse"]:.2f}')

        self.renderer.fov = self.cam_fov.get()
        self.lbl_fov.configure(text=f'{int(self.renderer.fov)}')

        self._update_cam_info()

    def _console_log(self, msg, cls='info'):
        """Write a message to the console with color coding."""
        colors = {'info': '#44aaff', 'ok': '#4488ff', 'err': '#ff4455', 'warn': '#ffcc00'}
        color = colors.get(cls, '#44aaff')
        self.console.configure(state='normal')
        self.console.insert('end', f'> {msg}\n')
        end_pos = self.console.index('end-1c')
        start_pos = self.console.index(f'{end_pos} linestart')
        self.console.tag_add(cls, start_pos, end_pos)
        self.console.tag_config(cls, foreground=color)
        self.console.see('end')
        self.console.configure(state='disabled')

    def _run_code(self):
        """Execute the code in the editor and update sprites."""
        # Close property editor
        if hasattr(self, '_prop_editor') and self._prop_editor is not None:
            try:
                self._prop_editor.destroy()
            except Exception:
                pass
            self._prop_editor = None

        code = self.code_editor.get('1.0', 'end-1c')
        self.sprites.clear()

        sprite = Sprite3D()
        self.sprites.append(sprite)
        self.active_sprite = sprite

        local_env = {
            'sprite': sprite,
            'Sprite3D': Sprite3D,
            'add_sprite': lambda s: self.sprites.append(s),
            'log': lambda msg: self._console_log(str(msg), 'info'),
            'math': math,
        }

        try:
            exec(code, {}, local_env)
            total = sum(s.get_triangle_count() for s in self.sprites)
            self._console_log(f'OK {len(self.sprites)} object(s), {total} triangle(s)', 'ok')
            self.tri_badge.configure(text=f'{total} triangles')
            if total > 64:
                self.tri_badge.configure(text_color='#ffcc00')
            else:
                self.tri_badge.configure(text_color='#4488ff')
            self.creator_view.refresh_object_list()
        except Exception as e:
            self._console_log(f'ERROR: {e}', 'err')
            self.sprites.clear()
            self.active_sprite = None
            if hasattr(self, '_prop_editor') and self._prop_editor is not None:
                try:
                    self._prop_editor.destroy()
                except Exception:
                    pass
                self._prop_editor = None
            self.creator_view.refresh_object_list()

    def _clear_code(self):
        """Clear the editor and reset sprites."""
        self.code_editor.delete('1.0', 'end')
        self.sprites.clear()
        self.active_sprite = None
        # Close any open property editor
        if hasattr(self, '_prop_editor') and self._prop_editor is not None:
            try:
                self._prop_editor.destroy()
            except Exception:
                pass
            self._prop_editor = None
        self.tri_badge.configure(text='0 triangles', text_color='#4488ff')
        self._console_log('Editor cleared.', 'info')
        self.creator_view.refresh_object_list()

    def _load_library_item(self, filepath):
        """Load a .sprite3d file from the library and add it to the scene."""
        sprite = Sprite3D.from_sprite3d_file(filepath)
        if sprite:
            self.sprites.append(sprite)
            self._console_log(f'Loaded {sprite.name} ({sprite.get_triangle_count()} triangles)', 'ok')
            self.creator_view.refresh_object_list()
            self._sync_code_from_sprites()
        else:
            self._console_log(f'Failed to load {filepath}', 'err')

    def _set_creator_color(self, color):
        """Set active creator color and update swatch highlights."""
        self.creator_color = color
        for sw in self.creator_swatches:
            idx = self.creator_swatches.index(sw)
            col = self.creator_colors[idx]
            sw.configure(fg_color=hex_to_tk_color(col), border_width=2,
                         border_color='#ffffff' if col == color else '#1a2530')

    def _toggle_palette(self, obj_type):
        """Toggle palette placement mode on/off for the given object type."""
        if self.palette_mode == obj_type:
            self._cancel_palette()
        else:
            self.palette_mode = obj_type
            for t, frame in self.palette_btns.items():
                frame.configure(border_color='#4466cc' if t == obj_type else '#1a2530')
            self.palette_status.configure(
                text=f'Click 3D viewport to place {obj_type.upper()}  [Esc to cancel]')
            self._console_log(f'Placement mode: click on 3D view to place {obj_type}', 'info')

    def _cancel_palette(self):
        """Cancel palette placement mode."""
        self.palette_mode = None
        for frame in self.palette_btns.values():
            frame.configure(border_color='#1a2530')
        if hasattr(self, 'palette_status'):
            self.palette_status.configure(text='Click an object to place')

    def _create_palette_sprite(self, obj_type):
        """Create a Sprite3D with the given primitive and return it."""
        s = Sprite3D()
        c = self.creator_color
        if obj_type == 'cube':
            s._cube(0, 0.5, 0, 1.0, 1.0, 1.0, c)
        elif obj_type == 'rect_prism':
            s._cube(0, 0.3, 0, 1.5, 0.6, 1.0, c)
        elif obj_type == 'tri_prism':
            s._triangular_prism(0, 0.4, 0, 1.2, 0.8, 1.0, c)
        elif obj_type == 'sphere':
            s._sphere(0, 0.4, 0, 0.5, 4, c)
        elif obj_type == 'rectangle':
            s._cube(0, 0.05, 0, 1.6, 0.1, 1.0, c)
        elif obj_type == 'square':
            s._cube(0, 0.05, 0, 1.0, 0.1, 1.0, c)
        elif obj_type == 'triangle':
            s._triangular_prism(0, 0.05, 0, 1.0, 0.1, 1.0, c)
        s.name = obj_type
        return s

    def _place_palette_object(self, world_x, world_z):
        """Create and place a palette object at the given world position."""
        if not self.palette_mode:
            return
        s = self._create_palette_sprite(self.palette_mode)
        s.set_position(world_x, world_z)
        self.sprites.append(s)
        self._sync_code_from_sprites()
        self.creator_view.refresh_object_list()

    def _delete_sprite(self, sprite):
        """Remove a sprite from the scene and refresh."""
        if sprite in self.sprites:
            self.sprites.remove(sprite)
            if self.active_sprite is sprite:
                self.active_sprite = None
            # Close property editor if it's editing this sprite
            if hasattr(self, '_prop_editor') and self._prop_editor is not None:
                try:
                    if self._prop_editor.sprite is sprite:
                        self._prop_editor.destroy()
                        self._prop_editor = None
                except Exception:
                    pass
            self._sync_code_from_sprites()
            self.creator_view.refresh_object_list()

    def _combine_selected(self):
        """Merge selected sprites into one object, preserving original triangle geometry
        and removing only truly internal faces."""
        selected = [s for s in self.sprites
                    if s in self.creator_view.obj_checkboxes
                    and self.creator_view.obj_checkboxes[s].get()]
        if len(selected) < 2:
            self._console_log('Select at least 2 objects to combine.', 'warn')
            return

        # Tag triangles by source
        tagged = []  # (triangle, source_index)
        sprite_tris = []
        for idx, sprite in enumerate(selected):
            tris = sprite.get_transformed_triangles()
            sprite_tris.append(tris)
            for t in tris:
                tagged.append((t, idx))

        keep = [True] * len(tagged)

        # Pass 1: opposing coplanar faces
        for i in range(len(tagged)):
            if not keep[i]:
                continue
            t1, src1 = tagged[i]
            for j in range(i + 1, len(tagged)):
                if not keep[j]:
                    continue
                t2, src2 = tagged[j]
                if src1 == src2:
                    continue
                if self._are_opposing_faces(t1, t2):
                    keep[i] = False
                    keep[j] = False
                    break

        # Pass 2: volume containment
        for i in range(len(tagged)):
            if not keep[i]:
                continue
            t, src = tagged[i]
            cx, cy, cz = t.get_center()
            for j, tris in enumerate(sprite_tris):
                if j == src:
                    continue
                if self._point_inside_mesh(cx, cy, cz, tris):
                    keep[i] = False
                    break

        # Keep survivors only
        visible = [tagged[i][0] for i in range(len(tagged)) if keep[i]]
        removed = len(tagged) - len(visible)

        if not visible:
            self._console_log('Combine failed: all faces would be internal.', 'err')
            return

        combined = Sprite3D()
        combined.name = 'combined'
        combined.type_str = 'COMBINED'
        combined.triangles = visible

        if selected[0].triangles:
            combined.set_color(selected[0].triangles[0].color)

        for s in selected:
            self.sprites.remove(s)
        self.sprites.append(combined)

        self._sync_code_from_sprites()
        self.creator_view.refresh_object_list()
        self._console_log(f'Combined {len(selected)} objects -> 1 '
                          f'({len(visible)} visible faces, {removed} internal removed).', 'ok')

    @staticmethod
    def _greedy_merge_quads(quads, nx, ny, nz):
        """Merge adjacent same-axis quads into larger rectangles (greedy meshing)."""
        # Group by axis and plane
        groups = {}
        face_defs = {
            0: ('x', 'ix', 'iy', 'iz'),   # +x
            1: ('x', 'ix', 'iy', 'iz'),   # -x
            2: ('y', 'iy', 'ix', 'iz'),   # +y
            3: ('y', 'iy', 'ix', 'iz'),   # -y
            4: ('z', 'iz', 'ix', 'iy'),   # +z
            5: ('z', 'iz', 'ix', 'iy'),   # -z
        }

        for axis, ix, iy, iz in quads:
            _, fixed_axis, u_axis, v_axis = face_defs[axis]
            fixed = {'ix': ix, 'iy': iy, 'iz': iz}[fixed_axis]
            u = {'ix': ix, 'iy': iy, 'iz': iz}[u_axis]
            v = {'ix': ix, 'iy': iy, 'iz': iz}[v_axis]
            key = (axis, fixed)
            groups.setdefault(key, set()).add((u, v))

        merged = []
        for (axis, fixed), cells in groups.items():
            _, _, u_axis, v_axis = face_defs[axis]
            max_u = {'ix': nx, 'iy': ny, 'iz': nz}[u_axis]
            max_v = {'ix': nx, 'iy': ny, 'iz': nz}[v_axis]
            # Build occupancy grid
            occupied = [[False] * max_v for _ in range(max_u)]
            for u, v in cells:
                occupied[u][v] = True

            # Greedy rectangle extraction
            for u in range(max_u):
                for v in range(max_v):
                    if not occupied[u][v]:
                        continue
                    # Expand v then u
                    v_end = v
                    while v_end + 1 < max_v and occupied[u][v_end + 1]:
                        v_end += 1
                    u_end = u
                    can_expand = True
                    while can_expand and u_end + 1 < max_u:
                        for vv in range(v, v_end + 1):
                            if not occupied[u_end + 1][vv]:
                                can_expand = False
                                break
                        if can_expand:
                            u_end += 1
                    # Clear merged strip
                    for uu in range(u, u_end + 1):
                        for vv in range(v, v_end + 1):
                            occupied[uu][vv] = False
                    merged.append((axis, u, u_end, v, v_end, fixed))

        return merged

    @staticmethod
    def _quad_to_tris(axis, u0, u1, v0, v1, fixed, min_x, min_y, min_z, vx, vy, vz, color):
        """Convert a merged quad (in voxel indices) into two world-space triangles."""
        # Voxel to world
        def world(axis, fixed_val, u_val, v_val):
            if axis == 0:    # +x: face at x = fixed+1
                return (min_x + (fixed_val + 1) * vx, min_y + u_val * vy, min_z + v_val * vz)
            elif axis == 1:  # -x: face at x = fixed
                return (min_x + fixed_val * vx, min_y + u_val * vy, min_z + v_val * vz)
            elif axis == 2:  # +y: face at y = fixed+1
                return (min_x + u_val * vx, min_y + (fixed_val + 1) * vy, min_z + v_val * vz)
            elif axis == 3:  # -y: face at y = fixed
                return (min_x + u_val * vx, min_y + fixed_val * vy, min_z + v_val * vz)
            elif axis == 4:  # +z: face at z = fixed+1
                return (min_x + u_val * vx, min_y + v_val * vy, min_z + (fixed_val + 1) * vz)
            else:            # -z: face at z = fixed
                return (min_x + u_val * vx, min_y + v_val * vy, min_z + fixed_val * vz)

        # World-space corners
        p00 = world(axis, fixed, u0, v0)
        p10 = world(axis, fixed, u1 + 1, v0)
        p01 = world(axis, fixed, u0, v1 + 1)
        p11 = world(axis, fixed, u1 + 1, v1 + 1)

        # Two triangles per quad
        tris = []
        if axis in (0, 2, 4):  # +x, +y, +z faces
            tris.append(Triangle3D(*p00, *p10, *p11, color))
            tris.append(Triangle3D(*p00, *p11, *p01, color))
        else:  # -x, -y, -z faces (flip winding)
            tris.append(Triangle3D(*p10, *p00, *p01, color))
            tris.append(Triangle3D(*p10, *p01, *p11, color))
        return tris

    @staticmethod
    def _sample_color_at_face(axis, u0, u1, v0, v1, fixed, min_x, min_y, min_z, vx, vy, vz, orig_tris):
        """Return the color of the nearest original triangle to a quad face center."""
        # Face center in world space
        if axis in (0, 1):
            w_coord = min_x + (fixed + (0.5 if axis == 0 else 0)) * vx
            cu = (u0 + u1 + 1) / 2.0
            cv = (v0 + v1 + 1) / 2.0
            cw_x, cw_y, cw_z = w_coord, min_y + cu * vy, min_z + cv * vz
        elif axis in (2, 3):
            w_coord = min_y + (fixed + (0.5 if axis == 2 else 0)) * vy
            cu = (u0 + u1 + 1) / 2.0
            cv = (v0 + v1 + 1) / 2.0
            cw_x, cw_y, cw_z = min_x + cu * vx, w_coord, min_z + cv * vz
        else:
            w_coord = min_z + (fixed + (0.5 if axis == 4 else 0)) * vz
            cu = (u0 + u1 + 1) / 2.0
            cv = (v0 + v1 + 1) / 2.0
            cw_x, cw_y, cw_z = min_x + cu * vx, min_y + cv * vy, w_coord

        best_color = 0x4466aa
        best_dist = float('inf')
        for t in orig_tris:
            cx, cy, cz = t.get_center()
            d2 = (cw_x - cx)**2 + (cw_y - cy)**2 + (cw_z - cz)**2
            if d2 < best_dist:
                best_dist = d2
                best_color = t.color
        return best_color

    @staticmethod
    def _point_inside_mesh(px, py, pz, triangles):
        """Return True if point (px,py,pz) is inside the closed triangle mesh."""
        # Jitter to avoid edge hits
        px += 0.000173
        py += 0.000311
        pz += 0.000527
        # Ray-cast in +x
        hits = 0
        for t in triangles:
            # Moller-Trumbore intersection
            e1x = t.x2 - t.x1
            e1y = t.y2 - t.y1
            e1z = t.z2 - t.z1
            e2x = t.x3 - t.x1
            e2y = t.y3 - t.y1
            e2z = t.z3 - t.z1

            # h = dir x e2, dir = (1,0,0)
            hx = 0.0
            hy = -e2z
            hz = e2y

            # u = (s*h) / det
            det = e1x * hx + e1y * hy + e1z * hz
            if abs(det) < 1e-10:
                continue
            inv_det = 1.0 / det

            sx = px - t.x1
            sy = py - t.y1
            sz = pz - t.z1

            u = (sx * hx + sy * hy + sz * hz) * inv_det
            if u < 0.0 or u > 1.0:
                continue

            # v = (dir*q) / det, dir = (1,0,0)
            qx = sy * e1z - sz * e1y
            qy = sz * e1x - sx * e1z
            qz = sx * e1y - sy * e1x

            v = (1.0 * qx) * inv_det
            if v < 0.0 or u + v > 1.0:
                continue

            # t = (e2*q) / det
            t_param = (e2x * qx + e2y * qy + e2z * qz) * inv_det
            if t_param > 1e-8:
                hits += 1

        return (hits % 2) == 1

    @staticmethod
    def _are_opposing_faces(t1, t2):
        """Return True if two triangles are coplanar, opposite-facing, and overlapping."""
        n1 = t1.get_normal()
        n1_len = math.sqrt(n1[0]**2 + n1[1]**2 + n1[2]**2)
        if n1_len < 1e-10:
            return False
        n1x, n1y, n1z = n1[0]/n1_len, n1[1]/n1_len, n1[2]/n1_len

        n2 = t2.get_normal()
        n2_len = math.sqrt(n2[0]**2 + n2[1]**2 + n2[2]**2)
        if n2_len < 1e-10:
            return False
        n2x, n2y, n2z = n2[0]/n2_len, n2[1]/n2_len, n2[2]/n2_len

        # Opposite normals
        dot = n1x * n2x + n1y * n2y + n1z * n2z
        if dot > -0.99:
            return False

        # Coplanar test
        d1 = n1x * t1.x1 + n1y * t1.y1 + n1z * t1.z1
        c2x = (t2.x1 + t2.x2 + t2.x3) / 3.0
        c2y = (t2.y1 + t2.y2 + t2.y3) / 3.0
        c2z = (t2.z1 + t2.z2 + t2.z3) / 3.0
        dist = abs(n1x * c2x + n1y * c2y + n1z * c2z - d1)
        if dist > 0.01:
            return False

        # Bounding box overlap
        abs_n = abs(n1x), abs(n1y), abs(n1z)
        if abs_n[0] >= abs_n[1] and abs_n[0] >= abs_n[2]:
            u_idx, v_idx = 1, 2
        elif abs_n[1] >= abs_n[0] and abs_n[1] >= abs_n[2]:
            u_idx, v_idx = 0, 2
        else:
            u_idx, v_idx = 0, 1

        def _bb(t, ui, vi):
            verts = [(t.x1, t.y1, t.z1), (t.x2, t.y2, t.z2), (t.x3, t.y3, t.z3)]
            us = [v[ui] for v in verts]
            vs = [v[vi] for v in verts]
            return min(us), max(us), min(vs), max(vs)

        u1_min, u1_max, v1_min, v1_max = _bb(t1, u_idx, v_idx)
        u2_min, u2_max, v2_min, v2_max = _bb(t2, u_idx, v_idx)

        return (u1_min < u2_max - 0.001 and u2_min < u1_max - 0.001 and
                v1_min < v2_max - 0.001 and v2_min < v1_max - 0.001)

    def _sync_code_from_sprites(self):
        """Regenerate code editor content from all sprites."""
        lines = ['# Generated from palette placement']
        for s in self.sprites:
            for t in s.triangles:
                hex_str = f'0x{t.color:06x}'
                wf_str = str(t.wireframe)
                lines.append(
                    f'sprite.add_triangle({t.x1:.2f},{t.y1:.2f},{t.z1:.2f}, '
                    f'{t.x2:.2f},{t.y2:.2f},{t.z2:.2f}, '
                    f'{t.x3:.2f},{t.y3:.2f},{t.z3:.2f}, {hex_str}, wireframe={wf_str})')
        code = '\n'.join(lines)
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', code)
        total = sum(s.get_triangle_count() for s in self.sprites)
        self.tri_badge.configure(text=f'{total} triangles')
        if total > 64:
            self.tri_badge.configure(text_color='#ffcc00')
        else:
            self.tri_badge.configure(text_color='#4488ff')

    def _export_cpp(self):
        """Generate C++ header from current sprites."""
        if not self.sprites:
            self.export_output.configure(state='normal')
            self.export_output.delete('1.0', 'end')
            self.export_output.insert('1.0', '// No sprites loaded. Run code first.')
            self.export_output.configure(state='disabled')
            self.tab_view.set('Export')
            return

        lines = [
            '#pragma once',
            '// Auto-generated by Pico Game Engine Studio',
            ''
        ]
        for idx, sprite in enumerate(self.sprites):
            name = (sprite.name or f'sprite_{idx}').replace(' ', '_').replace('-', '_')
            name = ''.join(c for c in name if c.isalnum() or c == '_')
            tris = sprite.get_transformed_triangles()
            lines.append(f'// {name} - {len(tris)} triangles')
            lines.append(f'inline void load_{name}(Sprite3D& sprite) {{')
            lines.append('    sprite.clear_triangles();')
            for t in tris:
                def fmt(n):
                    return f'{n:.4f}f'
                hex_str = f'0x{t.color:06x}'
                wf = 'true' if t.wireframe else 'false'
                lines.append(
                    f'    sprite.addTriangle({fmt(t.x1)},{fmt(t.y1)},{fmt(t.z1)}, '
                    f'{fmt(t.x2)},{fmt(t.y2)},{fmt(t.z2)}, '
                    f'{fmt(t.x3)},{fmt(t.y3)},{fmt(t.z3)}, {hex_str}, {wf});')
            lines.append('}')
            lines.append('')

        result = '\n'.join(lines)
        self.export_output.configure(state='normal')
        self.export_output.delete('1.0', 'end')
        self.export_output.insert('1.0', result)
        self.export_output.configure(state='disabled')
        self.tab_view.set('Export')
        self._console_log(f'Exported {len(self.sprites)} sprite(s) as C++', 'ok')

    def _import_sprite3d(self):
        """Import a .sprite3d binary file and add its triangles as a new sprite."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title='Import .sprite3d file',
            filetypes=[('Sprite3D files', '*.sprite3d'), ('All files', '*.*')],
        )
        if not filepath:
            return
        sprite = Sprite3D.from_sprite3d_file(filepath)
        if sprite is None:
            self._console_log(f'Failed to import: {filepath}', 'err')
            return
        self.sprites.append(sprite)
        self._sync_code_from_sprites()
        self.creator_view.refresh_object_list()
        self._console_log(
            f'Imported {sprite.name} ({sprite.get_triangle_count()} triangles)', 'ok')

    def _export_sprite3d(self):
        """Export the first active sprite as a .sprite3d binary file."""
        if not self.sprites:
            self._console_log('No sprites to export.', 'warn')
            return
        from tkinter import filedialog
        sprite = self.sprites[0]
        name = (sprite.name or 'sprite').replace(' ', '_')
        filepath = filedialog.asksaveasfilename(
            title='Export .sprite3d file',
            defaultextension='.sprite3d',
            initialfile=f'{name}.sprite3d',
            filetypes=[('Sprite3D files', '*.sprite3d'), ('All files', '*.*')],
        )
        if not filepath:
            return
        if sprite.to_sprite3d_file(filepath):
            self._console_log(
                f'Exported {name} ({sprite.get_triangle_count()} triangles) to {filepath}',
                'ok')
        else:
            self._console_log(f'Failed to export to {filepath}', 'err')

    def _copy_export(self):
        """Copy export output to clipboard."""
        text = self.export_output.get('1.0', 'end-1c')
        self.clipboard_clear()
        self.clipboard_append(text)
        self._console_log('Copied!', 'ok')


if __name__ == '__main__':
    app = Studio()
    app.mainloop()