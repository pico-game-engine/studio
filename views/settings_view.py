import customtkinter as ctk


class SettingsView:
    """Settings panel with render options, lighting sliders, camera settings, and stats."""

    def __init__(self, app, tab):
        self.app = app
        self.tab = tab
        self._build()

    def _build(self):
        tab = self.tab
        app = self.app

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(tab, corner_radius=0, fg_color='transparent')
        scroll.grid(row=0, column=0, sticky='nsew')
        scroll.grid_columnconfigure(0, weight=1)

        ro_group = ctk.CTkFrame(scroll, corner_radius=2)
        ro_group.grid(row=0, column=0, padx=8, pady=6, sticky='ew')
        ro_group.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ro_group, text='RENDER OPTIONS', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, padx=8, pady=4, sticky='w')

        app.check_vars = {}
        checks = [
            ('Wireframe edges', 'wireframe', True),
            ('Solid faces', 'solid', True),
            ('Show backfaces (debug)', 'backface', False),
            ('Ground grid', 'grid', True),
            ('World axes', 'axes', True),
            ('Face normals', 'normals', False),
            ('Per-face color', 'color', True),
        ]
        for i, (label, key, default) in enumerate(checks):
            var = ctk.BooleanVar(value=default)
            cb = ctk.CTkCheckBox(ro_group, text=label, variable=var,
                                  font=('Share Tech Mono', 10), checkbox_width=16, checkbox_height=16,
                                  command=app._update_opts)
            cb.grid(row=i + 1, column=0, padx=12, pady=2, sticky='w')
            app.check_vars[key] = var

        light_group = ctk.CTkFrame(scroll, corner_radius=2)
        light_group.grid(row=1, column=0, padx=8, pady=6, sticky='ew')
        light_group.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(light_group, text='LIGHTING', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, columnspan=3, padx=8, pady=4, sticky='w')

        ctk.CTkLabel(light_group, text='Ambient', font=('Share Tech Mono', 10),
                      text_color='#5a6a88').grid(row=1, column=0, padx=8, pady=2, sticky='w')
        app.light_ambient = ctk.CTkSlider(light_group, from_=0, to=100, command=app._update_opts)
        app.light_ambient.set(30)
        app.light_ambient.grid(row=1, column=1, padx=4, pady=2, sticky='ew')
        app.lbl_ambient = ctk.CTkLabel(light_group, text='0.30', font=('Share Tech Mono', 10),
                                         text_color='#4488ff', width=40)
        app.lbl_ambient.grid(row=1, column=2, padx=4, pady=2)

        ctk.CTkLabel(light_group, text='Diffuse', font=('Share Tech Mono', 10),
                      text_color='#5a6a88').grid(row=2, column=0, padx=8, pady=2, sticky='w')
        app.light_diffuse = ctk.CTkSlider(light_group, from_=0, to=100, command=app._update_opts)
        app.light_diffuse.set(70)
        app.light_diffuse.grid(row=2, column=1, padx=4, pady=2, sticky='ew')
        app.lbl_diffuse = ctk.CTkLabel(light_group, text='0.70', font=('Share Tech Mono', 10),
                                         text_color='#4488ff', width=40)
        app.lbl_diffuse.grid(row=2, column=2, padx=4, pady=2)

        cam_group = ctk.CTkFrame(scroll, corner_radius=2)
        cam_group.grid(row=2, column=0, padx=8, pady=6, sticky='ew')
        cam_group.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cam_group, text='CAMERA', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, columnspan=3, padx=8, pady=4, sticky='w')

        ctk.CTkLabel(cam_group, text='FOV', font=('Share Tech Mono', 10),
                      text_color='#5a6a88').grid(row=1, column=0, padx=8, pady=2, sticky='w')
        app.cam_fov = ctk.CTkSlider(cam_group, from_=30, to=120, command=app._update_opts)
        app.cam_fov.set(60)
        app.cam_fov.grid(row=1, column=1, padx=4, pady=2, sticky='ew')
        app.lbl_fov = ctk.CTkLabel(cam_group, text='60', font=('Share Tech Mono', 10),
                                     text_color='#4488ff', width=40)
        app.lbl_fov.grid(row=1, column=2, padx=4, pady=2)

        ctk.CTkLabel(cam_group, text='Near clip', font=('Share Tech Mono', 10),
                      text_color='#5a6a88').grid(row=2, column=0, padx=8, pady=2, sticky='w')
        app.cam_near = ctk.CTkEntry(cam_group, width=70, font=('Share Tech Mono', 10))
        app.cam_near.insert(0, '0.1')
        app.cam_near.grid(row=2, column=1, padx=4, pady=2, sticky='w')

        stat_group = ctk.CTkFrame(scroll, corner_radius=2)
        stat_group.grid(row=3, column=0, padx=8, pady=6, sticky='ew')
        stat_group.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(stat_group, text='STATS', font=('Share Tech Mono', 10, 'bold'),
                      text_color='#4466cc').grid(row=0, column=0, columnspan=2, padx=8, pady=4, sticky='w')

        app.stat_labels = {}
        for i, (label, key) in enumerate([('Triangles', 'tris'), ('Visible', 'vis'),
                                            ('Objects', 'objs'), ('FPS', 'fps')]):
            ctk.CTkLabel(stat_group, text=label, font=('Share Tech Mono', 10),
                          text_color='#5a6a88').grid(row=i + 1, column=0, padx=8, pady=2, sticky='w')
            lbl = ctk.CTkLabel(stat_group, text='0', font=('Share Tech Mono', 10),
                                text_color='#4488ff')
            lbl.grid(row=i + 1, column=1, padx=8, pady=2, sticky='e')
            app.stat_labels[key] = lbl
