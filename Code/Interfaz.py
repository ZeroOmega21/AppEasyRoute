import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os
import math 
# from utilidades import obtener_info_coordenada

class AppEasyRoute:
    def __init__(self, root, mapa, lugares_dict):
        self.root = root
        self.mapa = mapa 
        
        # CONFIGURACIÓN DE ESTILO Y TEMA 
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam') 
        
        # Paleta de Colores
        BG_PANEL = "#f0f2f5" 
        BG_CARD = "white"    
        ACCENT_COLOR = "#007AFF" 
        TEXT_COLOR = "#333333"
        
        self.root.configure(bg=BG_PANEL)
        
        # Configurar estilos de widgets
        self.estilo.configure("TFrame", background=BG_PANEL)
        self.estilo.configure("TLabel", background=BG_PANEL, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        self.estilo.configure("TLabelframe", background=BG_PANEL, foreground=TEXT_COLOR)
        self.estilo.configure("TLabelframe.Label", background=BG_PANEL, foreground="#555", font=("Segoe UI", 9, "bold"))
        self.estilo.configure("TRadiobutton", background=BG_PANEL, font=("Segoe UI", 10))
        self.estilo.configure("TButton", font=("Segoe UI", 10, "bold"), background="#e1e1e1")
        self.estilo.map("TButton", background=[("active", "#d0d0d0")])

        # DATOS
        self.lugares_interes_coords = lugares_dict
        self.lista_lugares_visibles = sorted(list(self.lugares_interes_coords.keys()))
        
        self.ruta_actual = []
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        self.modo_marcado = tk.StringVar(value="origen") 
        self.modo_transporte = tk.StringVar(value="caminar") 

        self.root.title("EasyRoute - Navegación Inteligente")
        self.root.geometry("1100x750")
        self.factor_escala = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Carga Imagen
        try:
            self.img_original = Image.open(os.path.join("img", "Mapa.png"))
            self.ancho_base, self.alto_base = self.img_original.size
        except:
            self.img_original = Image.new("RGB", (800, 600), "white")
            self.ancho_base, self.alto_base = (800, 600)

        # PANEL IZQUIERDO (CONTROLES)
        self.frame_controles = ttk.Frame(self.root, width=320, padding=20)
        self.frame_controles.pack(side="left", fill="y")
        
        # Título de la App
        lbl_titulo = ttk.Label(self.frame_controles, text="EasyRoute", font=("Segoe UI", 24, "bold"), foreground=ACCENT_COLOR)
        lbl_titulo.pack(pady=(0, 20), anchor="w")

        # SECCIÓN 1: HERRAMIENTA DE MARCADO
        lf_marcado = ttk.LabelFrame(self.frame_controles, text="📍 Herramienta de Mapa", padding=15)
        lf_marcado.pack(fill="x", pady=(0, 15))
        
        ttk.Radiobutton(lf_marcado, text="Fijar Origen (Click)", variable=self.modo_marcado, value="origen").pack(anchor="w", pady=2)
        ttk.Radiobutton(lf_marcado, text="Fijar Destino (Click)", variable=self.modo_marcado, value="destino").pack(anchor="w", pady=2)

        # SECCIÓN 2: PLANIFICADOR 
        lf_plan = ttk.LabelFrame(self.frame_controles, text="🗺️ Planificar Viaje", padding=15)
        lf_plan.pack(fill="x", pady=(0, 15))

        ttk.Label(lf_plan, text="Desde:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_origen = ttk.Combobox(lf_plan, values=self.lista_lugares_visibles, state="readonly", height=5)
        self.combo_origen.pack(pady=(2, 10), fill="x")
        self.combo_origen.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("origen"))

        ttk.Label(lf_plan, text="Hasta:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_destino = ttk.Combobox(lf_plan, values=self.lista_lugares_visibles, state="readonly", height=5)
        self.combo_destino.pack(pady=(2, 10), fill="x")
        self.combo_destino.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("destino"))
        
        ttk.Separator(lf_plan, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(lf_plan, text="Medio de Transporte:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Radiobutton(lf_plan, text="🚶 Caminar (5 km/h)", variable=self.modo_transporte, value="caminar").pack(anchor="w")
        ttk.Radiobutton(lf_plan, text="🚗 Auto (40 km/h)", variable=self.modo_transporte, value="auto").pack(anchor="w")

        # BOTONES DE ACCIÓN
        frame_botones = ttk.Frame(self.frame_controles)
        frame_botones.pack(fill="x", pady=(0, 20))
        
        self.btn_buscar = tk.Button(frame_botones, text="CALCULAR RUTA", bg=ACCENT_COLOR, fg="white", 
                                    font=("Segoe UI", 10, "bold"), relief="flat", pady=8,
                                    command=self.buscar_ruta_presionado)
        self.btn_buscar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_limpiar = ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_todo)
        self.btn_limpiar.pack(side="right", fill="x", padx=(5, 0))

        # TARJETA DE RESULTADOS (Diseño tipo Card)
        self.frame_resultado = tk.Frame(self.frame_controles, bg=BG_CARD, bd=1, relief="solid")
        self.frame_resultado.configure(highlightbackground="#cccccc", highlightthickness=1)
        self.frame_resultado.pack(fill="x", ipady=10)
        
        tk.Label(self.frame_resultado, text="ESTADO DEL VIAJE", bg=BG_CARD, fg="#888", font=("Segoe UI", 8, "bold")).pack(pady=(10, 5))
        
        self.lbl_resultado = tk.Label(self.frame_resultado, text="Selecciona puntos para comenzar.", 
                                      bg=BG_CARD, fg="#444", font=("Segoe UI", 10), justify="center")
        self.lbl_resultado.pack(padx=10, pady=5)

        # AREA DEL MAPA (DERECHA)
        self.frame_mapa = ttk.Frame(self.root)
        self.frame_mapa.pack(side="right", fill="both", expand=True)
        
        # Fondo oscuro para que resalte el mapa
        self.canvas_mapa = tk.Canvas(self.frame_mapa, bg="#2b2b2b", highlightthickness=0) 
        self.canvas_mapa.pack(fill="both", expand=True)
        
        self.canvas_mapa.bind('<Configure>', self.actualizar_mapa)
        self.canvas_mapa.bind('<Button-1>', self.manejar_clic_mapa)
        
        # EVENTO CLIC DERECHO
        # self.canvas_mapa.bind('<Button-3>', self.al_hacer_clic_derecho)

    # MÉTODO PARA CLIC DERECHO
    # def al_hacer_clic_derecho(self, event):
    #     """Llama a la función externa en utilidades.py"""
    #     coords = obtener_info_coordenada(
    #         event, 
    #         self.offset_x, 
    #         self.offset_y, 
    #         self.factor_escala, 
    #         self.ancho_base, 
    #         self.alto_base
    #     )
    #     
    #     if coords:
    #         # Dibujamos un punto MAGENTA temporal donde hiciste clic derecho
    #         rx, ry = coords
    #         # Convertimos de nuevo a pantalla solo para dibujar
    #         fx = (rx * self.factor_escala) + self.offset_x
    #         fy = (ry * self.factor_escala) + self.offset_y
    #         
    #         self.canvas_mapa.delete("debug_point") # Borra el anterior
    #         self.canvas_mapa.create_oval(fx-3, fy-3, fx+3, fy+3, fill="magenta", outline="white", tags="debug_point")

    # MÉTODOS DE LÓGICA Y DIBUJADO
    def formatear_nombre_visual(self, nombre_interno):
        if nombre_interno in self.lugares_interes_coords: return nombre_interno
        partes = nombre_interno.split('_') 
        if partes and partes[-1].isdigit(): partes.pop() 
        return " ".join(partes)

    def resetear_pin_manual(self, tipo):
        if tipo == "origen": self.nodo_origen_clic = None
        elif tipo == "destino": self.nodo_destino_clic = None
        self.redibujar_todo()

    def limpiar_todo(self):
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        self.ruta_actual = []
        self.combo_origen.set('')
        self.combo_destino.set('')
        self.lbl_resultado.config(text="Selecciona puntos para comenzar.", fg="#444")
        self.redibujar_todo()

    def manejar_clic_mapa(self, event):
        try:
            rx = int((event.x - self.offset_x) / self.factor_escala)
            ry = int((event.y - self.offset_y) / self.factor_escala)
        except: return

        nodo, dist = self.mapa.obtener_nodo_mas_cercano(rx, ry)
        if not nodo: return

        nombre_bonito = self.formatear_nombre_visual(nodo)
        accion = self.modo_marcado.get()
        
        if accion == "origen":
            self.nodo_origen_clic = nodo
            self.combo_origen.set(f"📍 {nombre_bonito}")
        elif accion == "destino":
            self.nodo_destino_clic = nodo
            self.combo_destino.set(f"🏁 {nombre_bonito}")

        self.redibujar_todo()
        origen = self.nodo_origen_clic if self.nodo_origen_clic else self.combo_origen.get()
        destino = self.nodo_destino_clic if self.nodo_destino_clic else self.combo_destino.get()
        if origen and destino: self.buscar_ruta_presionado()

    def calcular_distancia_total(self, ruta):
        METROS_POR_PIXEL = 0.5 
        dist_total_px = 0
        for i in range(len(ruta)-1):
            na, nb = ruta[i], ruta[i+1]
            xa, ya = self.mapa.obtener_coordenadas(na)
            xb, yb = self.mapa.obtener_coordenadas(nb)
            dist_total_px += math.sqrt((xb-xa)**2 + (yb-ya)**2)
        return dist_total_px * METROS_POR_PIXEL

    def buscar_ruta_presionado(self):
        origen = self.nodo_origen_clic if self.nodo_origen_clic else self.combo_origen.get()
        destino = self.nodo_destino_clic if self.nodo_destino_clic else self.combo_destino.get()
        if not origen or not destino: return
        
        modo = self.modo_transporte.get()
        ruta, tiempo_minutos = self.mapa.dijkstra(origen, destino, modo_transporte=modo)

        if not ruta:
            if modo == "auto" and ("Parque" in destino or "Picnic" in destino):
                msg = "⛔ ACCESO DENEGADO\nEl auto no puede entrar al Parque.\nSelecciona 'Caminar'."
                color_msg = "#d9534f" # Rojo
            else:
                msg = "❌ RUTA NO ENCONTRADA"
                color_msg = "#d9534f"
            
            self.lbl_resultado.config(text=msg, fg=color_msg, font=("Segoe UI", 10, "bold"))
            self.ruta_actual = []
        else:
            self.ruta_actual = ruta
            metros_reales = self.calcular_distancia_total(ruta)
            mins = int(tiempo_minutos)
            segs = int((tiempo_minutos - mins) * 60)
            
            if metros_reales >= 1000: texto_dist = f"{metros_reales/1000:.2f} km"
            else: texto_dist = f"{int(metros_reales)} m"

            self.lbl_resultado.config(
                text=f"✅ RUTA CALCULADA\n\n⏱ Tiempo: {mins} min {segs} s\n📏 Distancia: {texto_dist}\n🚗 Modo: {modo.upper()}",
                fg="#28a745", font=("Segoe UI", 10, "bold")
            )
        
        self.redibujar_todo()

    def actualizar_mapa(self, event):
        w, h = event.width, event.height
        if w < 10: return
        ratio = min(w / self.ancho_base, h / self.alto_base)
        self.factor_escala = ratio
        nw, nh = int(self.ancho_base * ratio), int(self.alto_base * ratio)
        self.offset_x, self.offset_y = (w - nw) // 2, (h - nh) // 2
        self.img_tk = ImageTk.PhotoImage(self.img_original.resize((nw, nh), Image.Resampling.LANCZOS))
        self.redibujar_todo()

    def redibujar_todo(self):
        self.canvas_mapa.delete("all")
        self.canvas_mapa.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.img_tk)

        # 1. Puntos de Interés (Naranjas con borde blanco grueso)
        for n, (bx, by) in self.lugares_interes_coords.items():
            fx, fy = (bx*self.factor_escala)+self.offset_x, (by*self.factor_escala)+self.offset_y
            # Sombra
            self.canvas_mapa.create_oval(fx-3, fy-3+2, fx+3, fy+3+2, fill="#000000", stipple="gray50", outline="")
            # Punto
            self.canvas_mapa.create_oval(fx-4, fy-4, fx+4, fy+4, fill="#FF9500", outline="white", width=2, tags="marcador_interes")

        # 2. Ruta con borde
        if self.ruta_actual and len(self.ruta_actual) > 1:
            coords = []
            for nodo in self.ruta_actual:
                raw_x, raw_y = self.mapa.obtener_coordenadas(nodo)
                coords.extend([(raw_x*self.factor_escala)+self.offset_x, (raw_y*self.factor_escala)+self.offset_y])
            
            # Borde
            self.canvas_mapa.create_line(*coords, fill="#004080", width=7, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            # Interior
            self.canvas_mapa.create_line(*coords, fill="#007AFF", width=4, arrow=tk.LAST, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # 3. Pines Manuales
        if self.nodo_origen_clic:
            ox, oy = self.mapa.obtener_coordenadas(self.nodo_origen_clic)
            self.dibujar_pin((ox*self.factor_escala)+self.offset_x, (oy*self.factor_escala)+self.offset_y, "#28a745", "A")
        if self.nodo_destino_clic:
            dx, dy = self.mapa.obtener_coordenadas(self.nodo_destino_clic)
            self.dibujar_pin((dx*self.factor_escala)+self.offset_x, (dy*self.factor_escala)+self.offset_y, "#dc3545", "B")

    def dibujar_pin(self, x, y, color, letra):
        # Sombra pin
        self.canvas_mapa.create_oval(x-6, y-3, x+6, y+3, fill="black", stipple="gray50", outline="")
        # Pin cuerpo
        self.canvas_mapa.create_line(x, y, x, y-25, width=3, fill=color, capstyle=tk.ROUND)
        self.canvas_mapa.create_oval(x-12, y-45, x+12, y-21, fill=color, outline="white", width=2)
        self.canvas_mapa.create_text(x, y-33, text=letra, fill="white", font=("Segoe UI", 10, "bold"))