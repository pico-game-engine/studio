"""Voxel editor tab with multi-face 2D slice grids."""

import math
import tkinter as tk
import customtkinter as ctk
from helpers.voxel_grid import VoxelGrid
from helpers.color import hex_to_tk_color


FACES = {
    'FRONT':  ('z',  1, 'x', 'y'),
    'BACK':   ('z', -1, 'x', 'y'),
    'RIGHT':  ('x',  1, 'z', 'y'),
    'LEFT':   ('x', -1, 'z', 'y'),
    'TOP':    ('y',  1, 'x', 'z'),
    'BOTTOM': ('y', -1, 'x', 'z'),
}


class VoxelView:
    """Multi-face 2D voxel slice editor with main-viewport paint toggle."""

    PALETTE = [
        0xffcf9c, 0x4466aa, 0x334488, 0x2d6e2d, 0x5c3d11,
        0xd4b896, 0x8b2020, 0xccbbaa, 0xaa8855, 0x00ff88,
        0xff4455, 0x44aaff, 0xffcc00, 0x666666, 0x111111,
        0xffffff, 0xff8800, 0x8800ff, 0x0088ff, 0x000000,
    ]

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self.grid = VoxelGrid(24, 32, 12, 0.06)
        self.current_layer = 0
        self.current_face = 'FRONT'
        self.current_color = self.PALETTE[0]
        self.tool = 'pencil'
        self.cell_size = 14
        self.voxel_paint_active = False
        self._mouse_down = False
        self._build()

    def _build(self):
        tab = self.tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=0)
        tab.grid_rowconfigure(2, weight=0)
        tab.grid_rowconfigure(3, weight=1)
        tab.grid_rowconfigure(4, weight=0)
        tab.grid_rowconfigure(5, weight=0)
        tab.grid_rowconfigure(6, weight=0)

        # Header
        hdr = ctk.CTkFrame(tab, height=28, corner_radius=0, fg_color='transparent')
        hdr.grid(row=0, column=0, sticky='ew', padx=4, pady=(4, 0))
        self.voxel_count_label = ctk.CTkLabel(hdr, text='0 voxels',
                                               font=('Share Tech Mono', 10),
                                               text_color='#5a6a88')
        self.voxel_count_label.pack(side='left', padx=8)
        dims = f'{self.grid.nx}x{self.grid.ny}x{self.grid.nz}  vs={self.grid.voxel_size:.2f}'
        ctk.CTkLabel(hdr, text=dims, font=('Share Tech Mono', 9),
                     text_color='#5a6a88').pack(side='right', padx=8)

        # Face selector
        fbar = ctk.CTkFrame(tab, height=32, corner_radius=0, fg_color='transparent')
        fbar.grid(row=1, column=0, sticky='ew', padx=4, pady=2)
        self.face_buttons = {}
        for face in ['FRONT', 'BACK', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM']:
            btn = ctk.CTkButton(fbar, text=face, width=56, height=24,
                                font=('Share Tech Mono', 9),
                                command=lambda f=face: self._set_face(f))
            btn.pack(side='left', padx=1)
            self.face_buttons[face] = btn
        self._update_face_highlight()

        # Layer nav
        lbar = ctk.CTkFrame(tab, height=28, corner_radius=0, fg_color='transparent')
        lbar.grid(row=2, column=0, sticky='ew', padx=4, pady=1)
        self.layer_label = ctk.CTkLabel(lbar, text='Layer: 0', font=('Share Tech Mono', 9),
                                         text_color='#5a6a88')
        self.layer_label.pack(side='left', padx=8)
        self.layer_btn_prev = ctk.CTkButton(lbar, text='<', width=24, height=20,
                                             font=('Share Tech Mono', 9),
                                             command=lambda: self._shift_layer(-1))
        self.layer_btn_prev.pack(side='left', padx=1)
        self.layer_slider = ctk.CTkSlider(lbar, from_=0, to=max(0, self.grid.nz - 1),
                                           width=160, command=self._on_layer_slider)
        self.layer_slider.set(0)
        self.layer_slider.pack(side='left', padx=4)
        self.layer_btn_next = ctk.CTkButton(lbar, text='>', width=24, height=20,
                                             font=('Share Tech Mono', 9),
                                             command=lambda: self._shift_layer(1))
        self.layer_btn_next.pack(side='left', padx=1)

        # Grid canvas
        cframe = ctk.CTkFrame(tab, corner_radius=0, fg_color='#0a0f0a')
        cframe.grid(row=3, column=0, sticky='nsew', padx=4, pady=2)
        cframe.grid_rowconfigure(0, weight=1)
        cframe.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(cframe, bg='#0a0f0a', highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', lambda e: setattr(self, '_mouse_down', False))
        self.canvas.bind('<Button-3>', self._on_right_click)
        self.canvas.bind('<B3-Motion>', self._on_right_drag)
        self.canvas.bind('<ButtonRelease-3>', lambda e: setattr(self, '_mouse_down', False))
        self.canvas.bind('<Configure>', self._on_resize)

        # Toolbar
        tbar = ctk.CTkFrame(tab, height=32, corner_radius=0, fg_color='transparent')
        tbar.grid(row=4, column=0, sticky='ew', padx=4, pady=1)
        self._build_toolbar(tbar)

        # Palette
        pframe = ctk.CTkFrame(tab, height=36, corner_radius=0, fg_color='transparent')
        pframe.grid(row=5, column=0, sticky='ew', padx=4, pady=1)
        self._build_palette(pframe)

        # Actions
        aframe = ctk.CTkFrame(tab, height=32, corner_radius=0, fg_color='transparent')
        aframe.grid(row=6, column=0, sticky='ew', padx=4, pady=(1, 4))
        self._build_actions(aframe)

        self._redraw()

    def _build_toolbar(self, parent):
        self.tool_buttons = {}
        for key, label in [('pencil', 'PENCIL'), ('eraser', 'ERASER'), ('fill', 'FILL')]:
            btn = ctk.CTkButton(parent, text=label, width=64, height=22,
                                font=('Share Tech Mono', 9),
                                command=lambda k=key: self._set_tool(k))
            btn.pack(side='left', padx=2)
            self.tool_buttons[key] = btn
        self._update_tool_highlight()

        ctk.CTkLabel(parent, text='|', text_color='#1a2530').pack(side='left', padx=4)
        self.paint_toggle_btn = ctk.CTkButton(parent, text='PAINT IN VIEWPORT', width=130, height=22,
                                               font=('Share Tech Mono', 9),
                                               command=self._toggle_paint_mode)
        self.paint_toggle_btn.pack(side='left', padx=4)
        self._update_paint_toggle()

        ctk.CTkButton(parent, text='CONVERT', width=70, height=22,
                       font=('Share Tech Mono', 9),
                       command=self._convert_selected).pack(side='left', padx=4)

        ctk.CTkLabel(parent, text='|', text_color='#1a2530').pack(side='left', padx=4)
        ctk.CTkLabel(parent, text='W:', font=('Share Tech Mono', 8),
                      text_color='#5a6a88').pack(side='left', padx=2)
        self.size_x_var = tk.StringVar(value=str(self.grid.nx))
        ctk.CTkEntry(parent, width=28, height=20, font=('Share Tech Mono', 8),
                     textvariable=self.size_x_var).pack(side='left', padx=1)
        ctk.CTkLabel(parent, text='H:', font=('Share Tech Mono', 8),
                      text_color='#5a6a88').pack(side='left', padx=1)
        self.size_y_var = tk.StringVar(value=str(self.grid.ny))
        ctk.CTkEntry(parent, width=28, height=20, font=('Share Tech Mono', 8),
                     textvariable=self.size_y_var).pack(side='left', padx=1)
        ctk.CTkLabel(parent, text='D:', font=('Share Tech Mono', 8),
                      text_color='#5a6a88').pack(side='left', padx=1)
        self.size_z_var = tk.StringVar(value=str(self.grid.nz))
        ctk.CTkEntry(parent, width=28, height=20, font=('Share Tech Mono', 8),
                     textvariable=self.size_z_var).pack(side='left', padx=1)
        ctk.CTkButton(parent, text='RSZ', width=36, height=20,
                       font=('Share Tech Mono', 8),
                       command=self._resize_grid).pack(side='left', padx=2)

    def _build_palette(self, parent):
        self.palette_frames = []
        for i, color in enumerate(self.PALETTE):
            f = ctk.CTkFrame(parent, width=22, height=22, corner_radius=2,
                             fg_color=hex_to_tk_color(color),
                             border_width=1, border_color='#1a2530')
            f.pack(side='left', padx=1, pady=2)
            f.bind('<Button-1>', lambda e, c=color, idx=i: self._pick_color(c, idx))
            f.bind('<Enter>', lambda e, f=f: f.configure(border_color='#ffffff'))
            f.bind('<Leave>', lambda e, f=f: f.configure(border_color='#1a2530'))
            self.palette_frames.append(f)
        self._update_palette_highlight()

    def _build_actions(self, parent):
        ctk.CTkButton(parent, text='SAVE', width=60, height=24,
                       font=('Share Tech Mono', 9),
                       command=self._save_sprite3d).pack(side='left', padx=3)
        ctk.CTkButton(parent, text='CLEAR', width=56, height=24,
                       font=('Share Tech Mono', 9),
                       fg_color='#442222', hover_color='#553333',
                       command=self._clear_grid).pack(side='left', padx=3)
        ctk.CTkButton(parent, text='MIRROR X', width=70, height=24,
                       font=('Share Tech Mono', 9),
                       command=self._mirror_x).pack(side='left', padx=3)

    def _face_info(self):
        """Return (axis, dir, u_axis, v_axis, n_u, n_v, n_fixed) for current face."""
        axis, direction, u_axis, v_axis = FACES[self.current_face]
        dims = {'x': self.grid.nx, 'y': self.grid.ny, 'z': self.grid.nz}
        return axis, direction, u_axis, v_axis, dims[u_axis], dims[v_axis], dims[axis]

    def _voxel_at(self, u, v):
        """Get voxel color at (u,v) on current face/layer, or None."""
        axis, direction, u_axis, v_axis, nu, nv, nf = self._face_info()
        if not (0 <= u < nu and 0 <= v < nv):
            return None
        idx = {'x': 0, 'y': 0, 'z': 0}
        idx[u_axis] = u
        idx[v_axis] = v
        idx[axis] = self.current_layer
        return self.grid.get(idx['x'], idx['y'], idx['z'])

    def _set_voxel(self, u, v, color=None):
        """Set or erase voxel at (u,v) on current face/layer."""
        axis, direction, u_axis, v_axis, nu, nv, nf = self._face_info()
        if not (0 <= u < nu and 0 <= v < nv):
            return
        idx = {'x': 0, 'y': 0, 'z': 0}
        idx[u_axis] = u
        idx[v_axis] = v
        idx[axis] = self.current_layer
        if color is None:
            self.grid.erase(idx['x'], idx['y'], idx['z'])
        else:
            self.grid.set(idx['x'], idx['y'], idx['z'], color)

    def _set_face(self, face):
        self.current_face = face
        self.current_layer = 0
        self._update_face_highlight()
        self._update_layer_slider()
        self._redraw()

    def _update_face_highlight(self):
        for f, btn in self.face_buttons.items():
            active = f == self.current_face
            btn.configure(fg_color='#224488' if active else '#1a1a2e',
                          border_color='#4488ff' if active else '#1a2530',
                          border_width=1)

    def _shift_layer(self, delta):
        _, _, _, _, _, _, nf = self._face_info()
        z = max(0, min(nf - 1, self.current_layer + delta))
        if z != self.current_layer:
            self.current_layer = z
            self.layer_slider.set(z)
            self._update_layer_label()
            self._redraw()

    def _on_layer_slider(self, val):
        z = int(round(float(val)))
        if z != self.current_layer:
            self.current_layer = z
            self._update_layer_label()
            self._redraw()

    def _update_layer_slider(self):
        _, _, _, _, _, _, nf = self._face_info()
        self.layer_slider.configure(to=max(0, nf - 1))
        self.layer_slider.set(0)
        self._update_layer_label()

    def _update_layer_label(self):
        axis, _, _, _, _, _, nf = self._face_info()
        self.layer_label.configure(text=f'{axis.upper()}={self.current_layer}/{nf-1}')

    def _cell_at(self, ex, ey):
        cs = self.cell_size
        _, _, u_axis, v_axis, nu, nv, _ = self._face_info()
        u = ex // cs
        v = (nv - 1) - (ey // cs)
        if 0 <= u < nu and 0 <= v < nv:
            return u, v
        return None

    def _on_click(self, e):
        self._mouse_down = True
        self._paint_at(e.x, e.y)

    def _on_drag(self, e):
        if self._mouse_down:
            self._paint_at(e.x, e.y)

    def _on_right_click(self, e):
        self._mouse_down = True
        self._erase_at(e.x, e.y)

    def _on_right_drag(self, e):
        if self._mouse_down:
            self._erase_at(e.x, e.y)

    def _paint_at(self, ex, ey):
        cell = self._cell_at(ex, ey)
        if not cell:
            return
        u, v = cell
        if self.tool == 'eraser':
            self._set_voxel(u, v, None)
        elif self.tool == 'fill':
            self._flood_fill(u, v)
        else:
            self._set_voxel(u, v, self.current_color)
        self._redraw()
        self._sync_sprite_to_viewport()

    def _erase_at(self, ex, ey):
        cell = self._cell_at(ex, ey)
        if not cell:
            return
        self._set_voxel(cell[0], cell[1], None)
        self._redraw()
        self._sync_sprite_to_viewport()

    def _flood_fill(self, su, sv):
        target = self._voxel_at(su, sv)
        if target == self.current_color:
            return
        axis, _, u_axis, v_axis, nu, nv, _ = self._face_info()
        stack = [(su, sv)]
        visited = set()
        while stack:
            u, v = stack.pop()
            if (u, v) in visited:
                continue
            if not (0 <= u < nu and 0 <= v < nv):
                continue
            if self._voxel_at(u, v) != target:
                continue
            visited.add((u, v))
            self._set_voxel(u, v, self.current_color)
            stack.extend([(u+1,v), (u-1,v), (u,v+1), (u,v-1)])
        self._redraw()

    def _on_resize(self, e=None):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw > 10 and ch > 10:
            _, _, _, _, nu, nv, _ = self._face_info()
            self.cell_size = max(6, min(cw // nu, ch // nv))
            self._redraw()

    def _redraw(self):
        self.canvas.delete('all')
        cs = self.cell_size
        _, _, _, _, nu, nv, _ = self._face_info()
        for u in range(nu):
            for v in range(nv):
                color = self._voxel_at(u, v)
                x1 = u * cs
                y1 = (nv - 1 - v) * cs
                x2, y2 = x1 + cs, y1 + cs
                if color is not None:
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                  fill=f'#{color:06x}', outline='', width=0)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                  fill='#0d120d', outline='#111811', width=1)
        self.voxel_count_label.configure(text=f'{self.grid.voxel_count()} voxels')

    def _toggle_paint_mode(self):
        self.voxel_paint_active = not self.voxel_paint_active
        self._update_paint_toggle()
        if self.voxel_paint_active:
            self._sync_sprite_to_viewport()
            self.app._console_log('Voxel paint mode ON — click in main viewport to place/erase.', 'info')
        else:
            self.app._console_log('Voxel paint mode OFF.', 'info')

    def _update_paint_toggle(self):
        if self.voxel_paint_active:
            self.paint_toggle_btn.configure(fg_color='#225522', text='PAINTING (click to stop)')
        else:
            self.paint_toggle_btn.configure(fg_color='#1a1a2e', text='PAINT IN VIEWPORT')

    def _convert_selected(self):
        """Convert the first non-voxel sprite in the scene to voxels."""
        for sprite in self.app.sprites:
            if getattr(sprite, 'type_str', '') != 'VOXEL_EDIT':
                self.load_from_sprite(sprite)
                return
        self.app._console_log('No sprite to convert.', 'warn')

    def _sync_sprite_to_viewport(self):
        """Rebuild the voxel sprite and add it to the main scene for 3D viewing."""
        # Remove old voxel sprite from scene
        self.app.sprites[:] = [s for s in self.app.sprites if getattr(s, 'type_str', '') != 'VOXEL_EDIT']
        if self.grid.voxel_count() > 0:
            sprite = self.grid.to_sprite3d('voxel_edit')
            sprite.type_str = 'VOXEL_EDIT'
            self.app.sprites.append(sprite)
        self.app.creator_view.refresh_object_list()

    def world_ray_place(self, origin, direction, erase=False):
        """Place/erase voxel from a world-space ray. Called by main viewport."""
        vs = self.grid.voxel_size
        off_x, off_z = 0.0, 0.0
        if self.grid.grid:
            xs = [p[0] for p in self.grid.grid]
            zs = [p[2] for p in self.grid.grid]
            off_x = -((min(xs) + max(xs) + 1) * vs * 0.5)
            off_z = -((min(zs) + max(zs) + 1) * vs * 0.5)

        ox = (origin[0] - off_x) / vs
        oy = origin[1] / vs
        oz = (origin[2] - off_z) / vs
        rx, ry, rz = direction

        nx, ny, nz = self.grid.nx, self.grid.ny, self.grid.nz
        vx = int(math.floor(ox))
        vy = int(math.floor(oy))
        vz = int(math.floor(oz))

        step_x = 1 if rx > 0 else -1
        step_y = 1 if ry > 0 else -1
        step_z = 1 if rz > 0 else -1

        t_max_x = ((vx + (1 if rx > 0 else 0)) - ox) / rx if abs(rx) > 1e-10 else float('inf')
        t_max_y = ((vy + (1 if ry > 0 else 0)) - oy) / ry if abs(ry) > 1e-10 else float('inf')
        t_max_z = ((vz + (1 if rz > 0 else 0)) - oz) / rz if abs(rz) > 1e-10 else float('inf')
        t_delta_x = 1.0 / abs(rx) if abs(rx) > 1e-10 else float('inf')
        t_delta_y = 1.0 / abs(ry) if abs(ry) > 1e-10 else float('inf')
        t_delta_z = 1.0 / abs(rz) if abs(rz) > 1e-10 else float('inf')

        prev_vx, prev_vy, prev_vz = vx, vy, vz

        for _ in range(200):
            if 0 <= vx < nx and 0 <= vy < ny and 0 <= vz < nz:
                if self.grid.get(vx, vy, vz) is not None:
                    if erase:
                        self.grid.erase(vx, vy, vz)
                    else:
                        tx = prev_vx
                        ty = prev_vy
                        tz = prev_vz
                        if 0 <= tx < nx and 0 <= ty < ny and 0 <= tz < nz:
                            self.grid.set(tx, ty, tz, self.current_color)
                    self._redraw()
                    self._sync_sprite_to_viewport()
                    return True
            if t_max_x <= t_max_y and t_max_x <= t_max_z:
                prev_vx, prev_vy, prev_vz = vx, vy, vz
                vx += step_x
                t_max_x += t_delta_x
            elif t_max_y <= t_max_z:
                prev_vx, prev_vy, prev_vz = vx, vy, vz
                vy += step_y
                t_max_y += t_delta_y
            else:
                prev_vx, prev_vy, prev_vz = vx, vy, vz
                vz += step_z
                t_max_z += t_delta_z

        if abs(ry) > 1e-10:
            t = -oy / ry
            if t > 0:
                wx = ox + rx * t
                wz = oz + rz * t
                tx = int(wx)
                tz = int(wz)
                if 0 <= tx < nx and 0 <= tz < nz:
                    self.grid.set(tx, 0, tz, self.current_color)
                    self._redraw()
                    self._sync_sprite_to_viewport()
                    return True
        return False

    def _set_tool(self, tool):
        self.tool = tool
        self._update_tool_highlight()

    def _update_tool_highlight(self):
        for key, btn in self.tool_buttons.items():
            active = key == self.tool
            btn.configure(fg_color='#224488' if active else '#1a1a2e',
                          border_color='#4488ff' if active else '#1a2530', border_width=1)

    def _pick_color(self, color, idx):
        self.current_color = color
        self.tool = 'pencil'
        self._update_tool_highlight()
        self._update_palette_highlight()

    def _update_palette_highlight(self):
        for i, f in enumerate(self.palette_frames):
            active = self.PALETTE[i] == self.current_color
            f.configure(border_color='#ffffff' if active else '#1a2530',
                        border_width=2 if active else 1)

    def load_from_sprite(self, sprite):
        """Populate voxel grid from a Sprite3D, auto-resizing grid to fit."""
        import math as _math
        aabb = sprite.get_aabb()
        vs = self.grid.voxel_size
        margin = 2
        nx = int((aabb[3] - aabb[0]) / vs) + margin
        ny = int((aabb[4] - aabb[1]) / vs) + margin
        nz = int((aabb[5] - aabb[2]) / vs) + margin
        nx = max(4, min(64, nx))
        ny = max(4, min(64, ny))
        nz = max(4, min(64, nz))
        min_x, min_y, min_z = aabb[0], aabb[1], aabb[2]
        self.grid = VoxelGrid(nx, ny, nz, vs)
        for t in sprite.triangles:
            nxn, nyn, nzn = t.get_normal()
            length = _math.sqrt(nxn*nxn + nyn*nyn + nzn*nzn)
            if length < 1e-10:
                continue
            nxn /= length; nyn /= length; nzn /= length
            # Rasterize triangle: sample all 3 vertices + center for coverage
            pts_world = [(t.x1,t.y1,t.z1), (t.x2,t.y2,t.z2), (t.x3,t.y3,t.z3),
                         (t.get_center())]
            for (wx, wy, wz) in pts_world:
                vx = wx - nxn * vs * 0.5
                vy = wy - nyn * vs * 0.5
                vz = wz - nzn * vs * 0.5
                ix = int((vx - min_x) / vs)
                iy = int((vy - min_y) / vs)
                iz = int((vz - min_z) / vs)
                if 0 <= ix < nx and 0 <= iy < ny and 0 <= iz < nz:
                    self.grid.set(ix, iy, iz, t.color)
            # Also rasterize the triangle's voxel bounding box for merged faces
            # Get all 3 vertices in voxel space
            vis = []
            for (wx, wy, wz) in [(t.x1,t.y1,t.z1), (t.x2,t.y2,t.z2), (t.x3,t.y3,t.z3)]:
                vx = wx - nxn * vs * 0.5
                vy = wy - nyn * vs * 0.5
                vz = wz - nzn * vs * 0.5
                ix = int((vx - min_x) / vs)
                iy = int((vy - min_y) / vs)
                iz = int((vz - min_z) / vs)
                vis.append((ix, iy, iz))
            # Fill bounding box of the 3 voxel-space vertices
            ix0 = max(0, min(v[0] for v in vis))
            ix1 = min(nx-1, max(v[0] for v in vis))
            iy0 = max(0, min(v[1] for v in vis))
            iy1 = min(ny-1, max(v[1] for v in vis))
            iz0 = max(0, min(v[2] for v in vis))
            iz1 = min(nz-1, max(v[2] for v in vis))
            for ix in range(ix0, ix1+1):
                for iy in range(iy0, iy1+1):
                    for iz in range(iz0, iz1+1):
                        self.grid.set(ix, iy, iz, t.color)
        self.size_x_var.set(str(nx))
        self.size_y_var.set(str(ny))
        self.size_z_var.set(str(nz))
        self.current_layer = 0
        self._update_layer_slider()
        # Remove original sprite from scene (replaced by voxel_edit)
        if sprite in self.app.sprites:
            self.app.sprites.remove(sprite)
        self._redraw()
        self._sync_sprite_to_viewport()
        self.app._console_log(
            f'Voxels: {sprite.get_triangle_count()} tris -> {self.grid.voxel_count()} voxels (vs={vs:.3f})', 'info')

    def _import_sprite3d(self):
        """Import a .sprite3d file, auto-resize grid, and populate voxels."""
        from tkinter import filedialog
        from sprite3d import Sprite3D
        import os
        path = filedialog.askopenfilename(
            filetypes=[('Sprite3D files', '*.sprite3d')],
            initialdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'library'),
            title='Import .sprite3d to voxels')
        if not path:
            return
        sprite = Sprite3D.from_sprite3d_file(path)
        if not sprite:
            self.app._console_log('Failed to load file.', 'err')
            return

        aabb = sprite.get_aabb()
        vs = self.grid.voxel_size
        margin = 2
        nx = int((aabb[3] - aabb[0]) / vs) + margin
        ny = int((aabb[4] - aabb[1]) / vs) + margin
        nz = int((aabb[5] - aabb[2]) / vs) + margin
        nx = max(4, min(64, nx))
        ny = max(4, min(64, ny))
        nz = max(4, min(64, nz))

        min_x, min_y, min_z = aabb[0], aabb[1], aabb[2]

        self.grid = VoxelGrid(nx, ny, nz, vs)
        for t in sprite.triangles:
            cx, cy, cz = t.get_center()
            nxn, nyn, nzn = t.get_normal()
            length = math.sqrt(nxn*nxn + nyn*nyn + nzn*nzn)
            if length < 1e-10:
                continue
            nxn /= length; nyn /= length; nzn /= length
            # Voxel center is offset from face by half voxel opposite normal
            vx = cx - nxn * vs * 0.5
            vy = cy - nyn * vs * 0.5
            vz = cz - nzn * vs * 0.5
            ix = int((vx - min_x) / vs)
            iy = int((vy - min_y) / vs)
            iz = int((vz - min_z) / vs)
            if 0 <= ix < nx and 0 <= iy < ny and 0 <= iz < nz:
                self.grid.set(ix, iy, iz, t.color)

        self.size_x_var.set(str(nx))
        self.size_y_var.set(str(ny))
        self.size_z_var.set(str(nz))
        self.current_layer = 0
        self._update_layer_slider()
        self._redraw()
        self._sync_sprite_to_viewport()
        name = os.path.splitext(os.path.basename(path))[0]
        self.app._console_log(f'Imported {name}: {sprite.get_triangle_count()} tris -> {self.grid.voxel_count()} voxels', 'ok')

    def _save_sprite3d(self):
        if self.grid.voxel_count() == 0:
            self.app._console_log('No voxels to save.', 'warn')
            return
        from tkinter import filedialog
        import os
        path = filedialog.asksaveasfilename(
            defaultextension='.sprite3d',
            filetypes=[('Sprite3D files', '*.sprite3d')],
            initialdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'library'),
            title='Save voxel sprite')
        if not path:
            return
        name = os.path.splitext(os.path.basename(path))[0]
        sprite = self.grid.to_sprite3d(name)
        if sprite.to_sprite3d_file(path):
            self.app._console_log(f'Saved {name} ({sprite.get_triangle_count()} triangles)', 'ok')

    def _clear_grid(self):
        self.grid.clear()
        self._sync_sprite_to_viewport()
        self._redraw()
        self.app._console_log('Grid cleared.', 'info')

    def _mirror_x(self):
        nx = self.grid.nx
        new_voxels = {}
        for (x, y, z), color in self.grid.grid.items():
            mx = nx - 1 - x
            new_voxels[(x, y, z)] = color
            new_voxels[(mx, y, z)] = color
        self.grid.grid = new_voxels
        self._sync_sprite_to_viewport()
        self._redraw()
        self.app._console_log('Mirrored across X axis.', 'info')

    def _resize_grid(self):
        try:
            nx = int(self.size_x_var.get())
            ny = int(self.size_y_var.get())
            nz = int(self.size_z_var.get())
        except ValueError:
            self.app._console_log('Resize: invalid dimensions.', 'err')
            return
        nx = max(2, min(64, nx))
        ny = max(2, min(64, ny))
        nz = max(2, min(64, nz))
        self.size_x_var.set(str(nx))
        self.size_y_var.set(str(ny))
        self.size_z_var.set(str(nz))
        old = dict(self.grid.grid)
        self.grid = VoxelGrid(nx, ny, nz, self.grid.voxel_size)
        for (x, y, z), color in old.items():
            if x < nx and y < ny and z < nz:
                self.grid.set(x, y, z, color)
        self.current_layer = min(self.current_layer, nz - 1)
        self._update_layer_slider()
        self._sync_sprite_to_viewport()
        self._redraw()
        self.app._console_log(f'Grid resized to {nx}x{ny}x{nz}.', 'info')
