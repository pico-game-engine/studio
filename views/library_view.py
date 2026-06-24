import os
import tkinter as tk
import customtkinter as ctk


class LibraryView:
    """Scrollable grid of .sprite3d files from the library directory."""

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

        # Discover .sprite3d files in the library directory
        studio_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        library_dir = os.path.join(studio_dir, 'library')
        files = []
        if os.path.isdir(library_dir):
            for fname in sorted(os.listdir(library_dir)):
                if fname.endswith('.sprite3d'):
                    fpath = os.path.join(library_dir, fname)
                    name = os.path.splitext(fname)[0]
                    size = os.path.getsize(fpath)
                    tri_count = size // 52
                    files.append((name, fpath, tri_count))

        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)

        if not files:
            empty = ctk.CTkLabel(scroll_frame, text='No .sprite3d files in library/',
                                  font=('Share Tech Mono', 11), text_color='#5a6a88')
            empty.grid(row=0, column=0, columnspan=2, padx=20, pady=40)

        for i, (name, fpath, tri_count) in enumerate(files):
            row = i // 2
            col = i % 2
            btn_frame = ctk.CTkFrame(scroll_frame, corner_radius=2, fg_color='#111622',
                                      border_color='#1a2530', border_width=1)
            btn_frame.grid(row=row, column=col, padx=4, pady=3, sticky='ew')
            btn_frame.grid_columnconfigure(0, weight=1)

            name_lbl = ctk.CTkLabel(btn_frame, text=name.upper(), font=('Share Tech Mono', 11, 'bold'),
                                     text_color='#c8d8e8')
            name_lbl.grid(row=0, column=0, padx=8, pady=(4, 0), sticky='w')

            desc_lbl = ctk.CTkLabel(btn_frame, text=f'{tri_count} triangles', font=('Share Tech Mono', 9),
                                     text_color='#5a6a88')
            desc_lbl.grid(row=1, column=0, padx=8, pady=(0, 4), sticky='w')

            btn_frame.bind('<Button-1>', lambda e, p=fpath: app._load_library_item(p))
            name_lbl.bind('<Button-1>', lambda e, p=fpath: app._load_library_item(p))
            desc_lbl.bind('<Button-1>', lambda e, p=fpath: app._load_library_item(p))

            def on_enter(e, f=btn_frame):
                f.configure(border_color='#4466cc')

            def on_leave(e, f=btn_frame):
                f.configure(border_color='#1a2530')

            btn_frame.bind('<Enter>', on_enter)
            btn_frame.bind('<Leave>', on_leave)
