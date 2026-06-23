import tkinter as tk
import customtkinter as ctk


class PresetsView:
    """Grid of clickable preset cards that load example sprites."""

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self._build()

    def _build(self):
        tab = self.tab
        app = self.app

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(tab, bg='#0c1510', highlightthickness=0, bd=0)
        scrollbar = ctk.CTkScrollbar(tab, orientation='vertical', command=canvas.yview)
        scroll_frame = ctk.CTkFrame(canvas, corner_radius=0, fg_color='transparent')
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        presets = [
            ('HUMANOID', 'height=1.8', 'humanoid'),
            ('TREE', 'height=2.0', 'tree'),
            ('HOUSE', 'w=2.0 h=2.5', 'house'),
            ('PILLAR', 'h=3.0 r=0.3', 'pillar'),
            ('WALL SEGMENT', 'custom triangles', 'wall'),
            ('SCENE', 'multiple objects', 'scene'),
            ('CRATE', 'simple box', 'crate'),
            ('CUSTOM TRIS', 'raw triangles', 'custom'),
            ('ZOMBIE SHAMBLER', 'arms forward', 'zombie_shambler'),
            ('ZOMBIE CRAWLER', 'hunched pose', 'zombie_crawler'),
            ('ZOMBIE STALKER', 'tall & eerie', 'zombie_stalker'),
            ('ZOMBIE HORDE', 'all three', 'zombie_scene'),
            ('PISTOL', 'compact handgun', 'pistol'),
            ('RIFLE', 'assault rifle', 'rifle'),
            ('SHOTGUN', 'pump action', 'shotgun'),
            ('ROCKET LAUNCHER', 'tube launcher', 'rocket_launcher'),
            ('CROSSBOW', 'bolt launcher', 'crossbow'),
            ('BULLET', 'projectile', 'bullet'),
            ('ARROW', 'projectile', 'arrow'),
            ('ROCKET', 'projectile', 'rocket'),
        ]

        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)

        for i, (name, desc, key) in enumerate(presets):
            row = i // 2
            col = i % 2
            btn_frame = ctk.CTkFrame(scroll_frame, corner_radius=2, fg_color='#111622',
                                      border_color='#1a2530', border_width=1)
            btn_frame.grid(row=row, column=col, padx=4, pady=3, sticky='ew')
            btn_frame.grid_columnconfigure(0, weight=1)

            name_lbl = ctk.CTkLabel(btn_frame, text=name, font=('Share Tech Mono', 11, 'bold'),
                                     text_color='#c8d8e8')
            name_lbl.grid(row=0, column=0, padx=8, pady=(4, 0), sticky='w')

            desc_lbl = ctk.CTkLabel(btn_frame, text=desc, font=('Share Tech Mono', 9),
                                     text_color='#5a6a88')
            desc_lbl.grid(row=1, column=0, padx=8, pady=(0, 4), sticky='w')

            btn_frame.bind('<Button-1>', lambda e, k=key: app._load_preset(k))
            name_lbl.bind('<Button-1>', lambda e, k=key: app._load_preset(k))
            desc_lbl.bind('<Button-1>', lambda e, k=key: app._load_preset(k))

            def on_enter(e, f=btn_frame):
                f.configure(border_color='#4466cc')

            def on_leave(e, f=btn_frame):
                f.configure(border_color='#1a2530')

            btn_frame.bind('<Enter>', on_enter)
            btn_frame.bind('<Leave>', on_leave)
