import customtkinter as ctk

from helpers.color import hex_to_tk_color


PALETTE_OBJECTS = [
    ('CUBE', 'cube'),
    ('RECT PRISM', 'rect_prism'),
    ('TRI PRISM', 'tri_prism'),
    ('SPHERE', 'sphere'),
    ('RECTANGLE', 'rectangle'),
    ('SQUARE', 'square'),
    ('TRIANGLE', 'triangle'),
]


OBJECT_ICONS = {
    'cube': '[ ]',
    'rect_prism': '[=]',
    'tri_prism': '/_\\',
    'sphere': '( )',
    'rectangle': '___',
    'square': '[ ]',
    'triangle': '/ \\',
}


class CreatorView:
    """Object palette for placing primitives on the 3D viewport."""

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self._build()

    def _build(self):
        tab = self.tab
        app = self.app

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_rowconfigure(6, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(tab, text='OBJECT PALETTE',
                              font=('Share Tech Mono', 11, 'bold'),
                              text_color='#4466cc')
        title.grid(row=0, column=0, padx=12, pady=(12, 4), sticky='w')

        # Palette scroll
        scroll = ctk.CTkScrollableFrame(tab, corner_radius=0, fg_color='transparent')
        scroll.grid(row=1, column=0, sticky='nsew', padx=8, pady=4)
        scroll.grid_columnconfigure(0, weight=1)

        app.palette_btns = {}
        for label, obj_type in PALETTE_OBJECTS:
            icon = OBJECT_ICONS.get(obj_type, '?')
            frame = ctk.CTkFrame(scroll, corner_radius=2, fg_color='#111622',
                                  border_color='#1a2530', border_width=1)
            frame.grid(row=len(app.palette_btns), column=0, padx=2, pady=2, sticky='ew')
            frame.grid_columnconfigure(0, weight=0)
            frame.grid_columnconfigure(1, weight=1)

            icon_lbl = ctk.CTkLabel(frame, text=icon, font=('Share Tech Mono', 14),
                                     text_color='#4488ff', width=30)
            icon_lbl.grid(row=0, column=0, padx=(8, 4), pady=6, sticky='w')

            name_lbl = ctk.CTkLabel(frame, text=label, font=('Share Tech Mono', 10),
                                     text_color='#c8d8e8')
            name_lbl.grid(row=0, column=1, padx=4, pady=6, sticky='w')

            frame.bind('<Button-1>', lambda e, t=obj_type: app._toggle_palette(t))
            icon_lbl.bind('<Button-1>', lambda e, t=obj_type: app._toggle_palette(t))
            name_lbl.bind('<Button-1>', lambda e, t=obj_type: app._toggle_palette(t))

            def on_enter(e, f=frame):
                f.configure(border_color='#4466cc')

            def on_leave(e, f=frame):
                active = app.palette_mode
                f.configure(border_color='#4466cc' if active else '#1a2530')

            frame.bind('<Enter>', on_enter)
            frame.bind('<Leave>', on_leave)
            app.palette_btns[obj_type] = frame

        # Color section
        color_section = ctk.CTkFrame(tab, corner_radius=0, fg_color='transparent')
        color_section.grid(row=2, column=0, sticky='ew', padx=12, pady=(8, 2))

        ctk.CTkLabel(color_section, text='COLOR', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').pack(anchor='w')

        colors_frame = ctk.CTkFrame(color_section, corner_radius=0, fg_color='transparent')
        colors_frame.pack(fill='x', pady=4)
        app.creator_swatches = []
        for col in app.creator_colors:
            sw = ctk.CTkButton(colors_frame, text='', width=18, height=18, corner_radius=2,
                                fg_color=hex_to_tk_color(col),
                                hover_color=hex_to_tk_color(col),
                                command=lambda c=col: app._set_creator_color(c))
            sw.pack(side='left', padx=1)
            app.creator_swatches.append(sw)

        # Status
        status_frame = ctk.CTkFrame(tab, corner_radius=0, height=24, fg_color='transparent')
        status_frame.grid(row=3, column=0, sticky='ew', padx=12, pady=(2, 10))

        app.palette_status = ctk.CTkLabel(status_frame, text='Click an object to place',
                                            font=('Share Tech Mono', 9), text_color='#5a6a88')
        app.palette_status.pack(side='left')

        # Separator
        sep = ctk.CTkFrame(tab, height=1, corner_radius=0, fg_color='#1a2530')
        sep.grid(row=4, column=0, sticky='ew', padx=12)

        # Object list
        obj_header = ctk.CTkFrame(tab, corner_radius=0, fg_color='transparent')
        obj_header.grid(row=5, column=0, sticky='ew', padx=12, pady=(6, 2))
        obj_header.grid_columnconfigure(0, weight=1)
        obj_header.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(obj_header, text='ON-SCREEN OBJECTS',
                      font=('Share Tech Mono', 11, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, sticky='w')

        combine_btn = ctk.CTkButton(obj_header, text='COMBINE', width=72, height=22,
                                     font=('Share Tech Mono', 9, 'bold'),
                                     fg_color='#1a253a', hover_color='#2a3a5a',
                                     text_color='#4488ff', border_width=1,
                                     border_color='#4466cc',
                                     command=app._combine_selected)
        combine_btn.grid(row=0, column=1, padx=(8, 0), sticky='e')

        self.obj_scroll = ctk.CTkScrollableFrame(tab, corner_radius=0, fg_color='transparent')
        self.obj_scroll.grid(row=6, column=0, sticky='nsew', padx=8, pady=4)
        self.obj_scroll.grid_columnconfigure(0, weight=1)

        self.obj_rows = []
        self.obj_checkboxes = {}
        self.refresh_object_list()

    def refresh_object_list(self):
        """Rebuild the list of on-screen objects from app.sprites."""
        for row in self.obj_rows:
            row.destroy()
        self.obj_rows.clear()
        self.obj_checkboxes.clear()
        app = self.app
        for idx, sprite in enumerate(app.sprites):
            frame = ctk.CTkFrame(self.obj_scroll, corner_radius=2, fg_color='#111622',
                                  border_color='#1a2530', border_width=1)
            frame.grid(row=len(self.obj_rows), column=0, padx=2, pady=2, sticky='ew')
            frame.grid_columnconfigure(2, weight=1)

            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(frame, text='', variable=var, width=16, height=16,
                                  corner_radius=2, border_width=1,
                                  fg_color='#4466cc', hover_color='#0066cc',
                                  border_color='#2a3a5a')
            cb.grid(row=0, column=0, padx=(6, 2), pady=4, sticky='w')
            self.obj_checkboxes[sprite] = var

            name = sprite.name or f'object_{idx}'
            tri_count = sprite.get_triangle_count()
            lbl = ctk.CTkLabel(frame, text=f'#{idx} {name}',
                                font=('Share Tech Mono', 10),
                                text_color='#c8d8e8')
            lbl.grid(row=0, column=1, padx=(2, 4), pady=4, sticky='w')

            info = ctk.CTkLabel(frame, text=f'{tri_count} tris',
                                font=('Share Tech Mono', 8),
                                text_color='#5a6a88')
            info.grid(row=0, column=2, padx=4, pady=4, sticky='e')

            del_btn = ctk.CTkButton(frame, text='X', width=22, height=22, corner_radius=2,
                                     font=('Share Tech Mono', 10, 'bold'),
                                     fg_color='#3a1515', hover_color='#5a2020',
                                     text_color='#ff4455',
                                     command=lambda s=sprite: app._delete_sprite(s))
            del_btn.grid(row=0, column=3, padx=(2, 6), pady=4, sticky='e')

            frame.bind('<Button-1>', lambda e, s=sprite: app._open_property_editor(s))
            lbl.bind('<Button-1>', lambda e, s=sprite: app._open_property_editor(s))
            info.bind('<Button-1>', lambda e, s=sprite: app._open_property_editor(s))

            self.obj_rows.append(frame)
