from tkinter import scrolledtext
import customtkinter as ctk


class CodeView:
    """Code editor tab with toolbar, editor, and console."""

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self._build()

    def _build(self):
        tab = self.tab
        app = self.app

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(tab, corner_radius=0, height=36)
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.grid_propagate(False)

        app.run_btn = ctk.CTkButton(toolbar, text='RUN', width=70, height=26,
                                     font=('Share Tech Mono', 11),
                                     fg_color='#001133', hover_color='#002255',
                                     text_color='#4488ff', command=app._run_code)
        app.run_btn.pack(side='left', padx=4, pady=4)

        app.clear_btn = ctk.CTkButton(toolbar, text='CLEAR', width=60, height=26,
                                       font=('Share Tech Mono', 11),
                                       command=app._clear_code)
        app.clear_btn.pack(side='left', padx=4, pady=4)

        app.tri_badge = ctk.CTkLabel(toolbar, text='0 triangles',
                                      font=('Share Tech Mono', 10),
                                      text_color='#4488ff')
        app.tri_badge.pack(side='right', padx=8, pady=4)

        app.code_editor = scrolledtext.ScrolledText(
            tab, bg='#070d0a', fg='#4488ff',
            insertbackground='#4488ff',
            font=('Share Tech Mono', 12),
            bd=0, highlightthickness=0,
            wrap='none',
            selectbackground='#001133',
        )
        app.code_editor.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        app.code_editor.insert('1.0',
            '# Sprite3D definition\n'
            '# Available: sprite, Sprite3D, add_sprite, log\n'
            '#\n'
            '# sprite.create_humanoid(height)\n'
            '# sprite.create_tree(height)\n'
            '# sprite.create_house(width, height)\n'
            '# sprite.create_pillar(height, radius)\n'
            '# sprite.add_triangle(x1,y1,z1, x2,y2,z2, x3,y3,z3, color)\n'
            '# sprite.clear_triangles()\n'
            '# sprite.set_position(x, z)\n'
            '# sprite.set_rotation(angleRad)\n'
            '# sprite.set_scale(factor)\n'
            '#\n'
            '# Press RUN or Ctrl+Enter to render\n')

        app.console = scrolledtext.ScrolledText(
            tab, height=6, bg='#070d0a', fg='#5a6a88',
            insertbackground='#4488ff',
            font=('Share Tech Mono', 10),
            bd=0, highlightthickness=0,
            wrap='word',
            state='disabled',
        )
        app.console.grid(row=2, column=0, sticky='ew')
        app._console_log('Pico Game Engine Studio ready. Write code and press RUN.', 'info')
