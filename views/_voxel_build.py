    def _build(self):
        tab = self.tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=0)
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_rowconfigure(3, weight=0)
        tab.grid_rowconfigure(4, weight=0)
        tab.grid_rowconfigure(5, weight=0)

        header = ctk.CTkFrame(tab, height=30, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))
        self._build_header(header)

        zframe = ctk.CTkFrame(tab, height=32, corner_radius=0, fg_color="transparent")
        zframe.grid(row=1, column=0, sticky="ew", padx=4, pady=2)
        self._build_z_nav(zframe)

        main = ctk.CTkFrame(tab, corner_radius=0, fg_color="#070d0a")
        main.grid(row=2, column=0, sticky="nsew", padx=4, pady=2)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=0)
        main.grid_rowconfigure(0, weight=1)

        vp = ctk.CTkFrame(main, corner_radius=0, fg_color="#070d0a")
        vp.grid(row=0, column=0, sticky="nsew")
        vp.grid_rowconfigure(0, weight=1)
        vp.grid_columnconfigure(0, weight=1)

        self.canvas_3d = tk.Canvas(vp, bg="#070d0a", highlightthickness=0, bd=0)
        self.canvas_3d.grid(row=0, column=0, sticky="nsew")

        sf = ctk.CTkFrame(main, width=180, corner_radius=0, fg_color="#0a0f0a")
        sf.grid(row=0, column=1, sticky="ns")
        sf.grid_propagate(False)
        ctk.CTkLabel(sf, text="SLICE Z", font=("Share Tech Mono", 9), text_color="#5a6a88").pack(pady=(4,0))
        self.slice_canvas = tk.Canvas(sf, bg="#0a0f0a", highlightthickness=0, bd=0, width=170, height=200)
        self.slice_canvas.pack(padx=4, pady=4)
        self._draw_slice()
