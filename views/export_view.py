from tkinter import scrolledtext
import customtkinter as ctk


class ExportView:
    """Export tab with .sprite3d import/export, C++ header generation, and clipboard copy."""

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self._build()

    def _build(self):
        tab = self.tab
        app = self.app

        tab.grid_rowconfigure(3, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # .sprite3d binary
        bin_group = ctk.CTkFrame(tab, corner_radius=2)
        bin_group.grid(row=0, column=0, padx=8, pady=6, sticky='ew')
        bin_group.grid_columnconfigure(0, weight=1)
        bin_group.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bin_group, text='.SPRITE3D FILES', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, columnspan=2,
                                                  padx=8, pady=4, sticky='w')

        ctk.CTkLabel(bin_group,
                      text='Binary format (raw Triangle3D structs) for the C++ engine.',
                      font=('Share Tech Mono', 10), text_color='#5a6a88',
                      justify='left').grid(row=1, column=0, columnspan=2,
                                           padx=8, pady=2, sticky='w')

        app.btn_import_sprite3d = ctk.CTkButton(bin_group, text='IMPORT .SPRITE3D',
                                                 font=('Share Tech Mono', 11),
                                                 fg_color='#001133', hover_color='#002255',
                                                 text_color='#44aaff',
                                                 command=app._import_sprite3d)
        app.btn_import_sprite3d.grid(row=2, column=0, padx=8, pady=8, sticky='ew')

        app.btn_export_sprite3d = ctk.CTkButton(bin_group, text='EXPORT .SPRITE3D',
                                                 font=('Share Tech Mono', 11),
                                                 fg_color='#001133', hover_color='#002255',
                                                 text_color='#4488ff',
                                                 command=app._export_sprite3d)
        app.btn_export_sprite3d.grid(row=2, column=1, padx=8, pady=8, sticky='ew')

        # C++ header
        cpp_group = ctk.CTkFrame(tab, corner_radius=2)
        cpp_group.grid(row=1, column=0, padx=8, pady=6, sticky='ew')
        cpp_group.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(cpp_group, text='EXPORT AS C++ HEADER', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, padx=8, pady=4, sticky='w')

        ctk.CTkLabel(cpp_group,
                      text="Generates a .hpp file with your sprite's triangles as inline C++.",
                      font=('Share Tech Mono', 10), text_color='#5a6a88',
                      justify='left').grid(row=1, column=0, padx=8, pady=2, sticky='w')

        app.gen_btn = ctk.CTkButton(cpp_group, text='GENERATE C++ HEADER',
                                      font=('Share Tech Mono', 11),
                                      fg_color='#001133', hover_color='#002255',
                                      text_color='#4488ff', command=app._export_cpp)
        app.gen_btn.grid(row=2, column=0, padx=8, pady=8, sticky='ew')

        # Output
        out_group = ctk.CTkFrame(tab, corner_radius=2)
        out_group.grid(row=3, column=0, padx=8, pady=6, sticky='nsew')
        out_group.grid_rowconfigure(1, weight=1)
        out_group.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(out_group, text='OUTPUT', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, padx=8, pady=4, sticky='w')

        app.export_output = scrolledtext.ScrolledText(
            out_group, bg='#070d0a', fg='#5a6a88',
            insertbackground='#4488ff',
            font=('Share Tech Mono', 10),
            bd=0, highlightthickness=0,
            wrap='none',
            state='disabled',
        )
        app.export_output.grid(row=1, column=0, sticky='nsew')

        copy_btn = ctk.CTkButton(out_group, text='COPY TO CLIPBOARD',
                                  font=('Share Tech Mono', 10),
                                  command=app._copy_export)
        copy_btn.grid(row=2, column=0, padx=8, pady=4, sticky='ew')
