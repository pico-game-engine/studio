import math
import customtkinter as ctk
from typing import Callable

import tkinter as tk
from helpers.color import hex_to_tk_color, SAMPLE_COLORS


class PropertyEditor(ctk.CTkToplevel):
    """Floating window to edit a sprite's position, scale, color, and individual faces."""

    def __init__(self, app, sprite, on_update: Callable):
        """Open editor for the given sprite. on_update is called after changes."""
        super().__init__(app)
        self.app = app
        self.sprite = sprite
        self.on_update = on_update

        self.title(f'Edit: {sprite.name or "sprite"}')
        self.geometry('480x520')
        self.minsize(400, 400)
        self.configure(fg_color='#0a1a10')
        self._build()

    def _build(self):
        """Build the property editor UI."""
        """Build the property editor UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Object properties
        props_frame = ctk.CTkFrame(self, corner_radius=0, fg_color='transparent')
        props_frame.grid(row=0, column=0, sticky='ew', padx=12, pady=(10, 4))
        props_frame.grid_columnconfigure(1, weight=1)

        row = 0
        ctk.CTkLabel(props_frame, text='OBJECT', font=('Share Tech Mono', 11, 'bold'),
                      text_color='#4466cc').grid(row=row, column=0, columnspan=3, sticky='w', pady=(0, 6))

        row += 1
        ctk.CTkLabel(props_frame, text='Pos X', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).grid(row=row, column=0, sticky='w')
        self.pos_x_var = ctk.DoubleVar(value=self.sprite.position['x'])
        ctk.CTkSlider(props_frame, from_=-8, to=8, variable=self.pos_x_var,
                       command=lambda v: self._on_change()).grid(row=row, column=1, sticky='ew', padx=6)
        self.pos_x_lbl = ctk.CTkLabel(props_frame, text=f'{self.sprite.position["x"]:.2f}',
                                       font=('Share Tech Mono', 9), text_color='#4488ff', width=40)
        self.pos_x_lbl.grid(row=row, column=2, sticky='e')

        row += 1
        ctk.CTkLabel(props_frame, text='Pos Y', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).grid(row=row, column=0, sticky='w')
        self.pos_y_var = ctk.DoubleVar(value=self.sprite.position.get('y', 0.0))
        ctk.CTkSlider(props_frame, from_=-8, to=8, variable=self.pos_y_var,
                       command=lambda v: self._on_change()).grid(row=row, column=1, sticky='ew', padx=6)
        self.pos_y_lbl = ctk.CTkLabel(props_frame, text=f'{self.sprite.position.get("y", 0.0):.2f}',
                                       font=('Share Tech Mono', 9), text_color='#4488ff', width=40)
        self.pos_y_lbl.grid(row=row, column=2, sticky='e')

        row += 1
        ctk.CTkLabel(props_frame, text='Pos Z', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).grid(row=row, column=0, sticky='w')
        self.pos_z_var = ctk.DoubleVar(value=self.sprite.position['z'])
        ctk.CTkSlider(props_frame, from_=-8, to=8, variable=self.pos_z_var,
                       command=lambda v: self._on_change()).grid(row=row, column=1, sticky='ew', padx=6)
        self.pos_z_lbl = ctk.CTkLabel(props_frame, text=f'{self.sprite.position["z"]:.2f}',
                                       font=('Share Tech Mono', 9), text_color='#4488ff', width=40)
        self.pos_z_lbl.grid(row=row, column=2, sticky='e')

        row += 1
        ctk.CTkLabel(props_frame, text='Scale', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).grid(row=row, column=0, sticky='w')
        self.scale_var = ctk.DoubleVar(value=self.sprite.scale_factor)
        ctk.CTkSlider(props_frame, from_=0.1, to=4.0, variable=self.scale_var,
                       command=lambda v: self._on_change()).grid(row=row, column=1, sticky='ew', padx=6)
        self.scale_lbl = ctk.CTkLabel(props_frame, text=f'{self.sprite.scale_factor:.2f}',
                                       font=('Share Tech Mono', 9), text_color='#4488ff', width=40)
        self.scale_lbl.grid(row=row, column=2, sticky='e')

        row += 1
        ctk.CTkLabel(props_frame, text='Rot Y', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).grid(row=row, column=0, sticky='w')
        deg = self.sprite.rotation_y * 180 / math.pi
        self.rot_var = ctk.DoubleVar(value=deg)
        ctk.CTkSlider(props_frame, from_=-180, to=180, variable=self.rot_var,
                       command=lambda v: self._on_change()).grid(row=row, column=1, sticky='ew', padx=6)
        self.rot_lbl = ctk.CTkLabel(props_frame, text=f'{deg:.0f}',
                                     font=('Share Tech Mono', 9), text_color='#4488ff', width=40)
        self.rot_lbl.grid(row=row, column=2, sticky='e')

        # Overall color
        row += 1
        color_frame = ctk.CTkFrame(props_frame, fg_color='transparent')
        color_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=(6, 0))
        color_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(color_frame, text='Color', font=('Share Tech Mono', 9),
                      text_color='#5a6a88', width=42).pack(side='left')

        # Color swatch palette
        swatch_frame = ctk.CTkFrame(color_frame, fg_color='transparent')
        swatch_frame.pack(side='left', padx=4)
        for col in SAMPLE_COLORS:
            sw = ctk.CTkButton(swatch_frame, text='', width=16, height=16, corner_radius=2,
                                fg_color=hex_to_tk_color(col),
                                hover_color=hex_to_tk_color(col),
                                command=lambda c=col: self._set_overall_color(c))
            sw.pack(side='left', padx=1)

        # Separator
        sep = ctk.CTkFrame(self, height=1, corner_radius=0, fg_color='#1a2530')
        sep.grid(row=1, column=0, sticky='ew', padx=12, pady=6)

        # Face list
        face_header = ctk.CTkFrame(self, corner_radius=0, fg_color='transparent')
        face_header.grid(row=2, column=0, sticky='ew', padx=12, pady=(0, 2))
        face_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(face_header, text='FACES', font=('Share Tech Mono', 11, 'bold'),
                      text_color='#4466cc').pack(side='left')

        self.page_size = 64
        self.face_page = 0
        self.face_rows = []

        page_bar = ctk.CTkFrame(face_header, fg_color='transparent')
        page_bar.pack(side='right')
        self.page_prev = ctk.CTkButton(page_bar, text='<', width=28, height=20,
                                        font=('Share Tech Mono', 10),
                                        command=self._prev_page)
        self.page_prev.pack(side='left', padx=1)
        self.page_label = ctk.CTkLabel(page_bar, text='', font=('Share Tech Mono', 9),
                                        text_color='#4488ff', width=30)
        self.page_label.pack(side='left', padx=1)
        self.page_next = ctk.CTkButton(page_bar, text='>', width=28, height=20,
                                        font=('Share Tech Mono', 10),
                                        command=self._next_page)
        self.page_next.pack(side='left', padx=1)

        self.face_scroll = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color='transparent')
        self.face_scroll.grid(row=3, column=0, sticky='nsew', padx=8, pady=4)
        self.face_scroll.grid_columnconfigure(1, weight=1)

        self._rebuild_face_list()

    def _add_face_row(self, idx, tri):
        """Add a row for an individual face/triangle."""
        row_frame = ctk.CTkFrame(self.face_scroll, corner_radius=0, fg_color='#111622',
                                  border_color='#1a2530', border_width=1)
        row_frame.grid(row=len(self.face_rows), column=0, sticky='ew', pady=1)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(3, weight=0)

        lbl = ctk.CTkLabel(row_frame, text=f'#{idx}', font=('Share Tech Mono', 9),
                            text_color='#5a6a88', width=22)
        lbl.grid(row=0, column=0, padx=(6, 2), pady=3, sticky='w')

        cx, cy, cz = tri.get_center()
        pos_lbl = ctk.CTkLabel(row_frame, text=f'({cx:.2f}, {cy:.2f}, {cz:.2f})',
                                font=('Share Tech Mono', 7), text_color='#3a5a48', width=100)
        pos_lbl.grid(row=0, column=1, padx=2, pady=3, sticky='w')

        color_btn = ctk.CTkButton(row_frame, text='', width=16, height=16, corner_radius=2,
                                   fg_color=hex_to_tk_color(tri.color),
                                   hover_color=hex_to_tk_color(tri.color))
        color_btn.grid(row=0, column=2, padx=4, pady=3, sticky='e')
        row_frame._color_btn = color_btn

        picker_canvas = tk.Canvas(row_frame, width=195, height=12, bg='#111622',
                                   highlightthickness=0, cursor='hand2')
        picker_canvas.grid(row=0, column=3, padx=(0, 6), pady=2, sticky='e')
        for ci, col in enumerate(SAMPLE_COLORS):
            x = ci * 13 + 1
            picker_canvas.create_rectangle(x, 1, x + 10, 11,
                                           fill=hex_to_tk_color(col), outline='')

        def on_picker_click(event, t=tri, b=color_btn):
            ci = min(max((event.x - 1) // 13, 0), len(SAMPLE_COLORS) - 1)
            c = SAMPLE_COLORS[ci]
            t.color = c
            b.configure(fg_color=hex_to_tk_color(c))
            self._on_change()
        picker_canvas.bind('<Button-1>', on_picker_click)

        self.face_rows.append(row_frame)

    def _set_overall_color(self, color):
        """Apply a uniform color to all triangles in the sprite."""
        for tri in self.sprite.triangles:
            tri.color = color
        for row in self.face_rows:
            btn = getattr(row, '_color_btn', None)
            if btn:
                btn.configure(fg_color=hex_to_tk_color(color))
        self._on_change()

    def _refresh_face_swatches(self):
        """Rebuild face list to reflect new colors."""
        self._rebuild_face_list()

    def _on_change(self):
        """Apply property changes to the sprite and notify the app."""
        self.sprite.position['x'] = self.pos_x_var.get()
        self.sprite.position['y'] = self.pos_y_var.get()
        self.sprite.position['z'] = self.pos_z_var.get()
        self.sprite.scale_factor = self.scale_var.get()
        self.sprite.rotation_y = self.rot_var.get() * math.pi / 180.0

        self.pos_x_lbl.configure(text=f'{self.sprite.position["x"]:.2f}')
        self.pos_y_lbl.configure(text=f'{self.sprite.position["y"]:.2f}')
        self.pos_z_lbl.configure(text=f'{self.sprite.position["z"]:.2f}')
        self.scale_lbl.configure(text=f'{self.sprite.scale_factor:.2f}')
        self.rot_lbl.configure(text=f'{self.sprite.rotation_y * 180 / math.pi:.0f}')

    def _rebuild_face_list(self):
        """Clear and re-render faces for the current page."""
        for row in self.face_rows:
            row.destroy()
        self.face_rows.clear()

        total = len(self.sprite.triangles)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        start = self.face_page * self.page_size
        end = min(start + self.page_size, total)

        for idx in range(start, end):
            tri = self.sprite.triangles[idx]
            self._add_face_row(idx, tri)

        self.page_label.configure(text=f'{self.face_page + 1}/{total_pages}')
        self.page_prev.configure(state='normal' if self.face_page > 0 else 'disabled')
        self.page_next.configure(state='normal' if self.face_page + 1 < total_pages else 'disabled')

    def _prev_page(self):
        """Go to previous page of faces."""
        if self.face_page > 0:
            self.face_page -= 1
            self._rebuild_face_list()

    def _next_page(self):
        """Go to next page of faces."""
        total_pages = max(1, (len(self.sprite.triangles) + self.page_size - 1) // self.page_size)
        if self.face_page + 1 < total_pages:
            self.face_page += 1
            self._rebuild_face_list()
