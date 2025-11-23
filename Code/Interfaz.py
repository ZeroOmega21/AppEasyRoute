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
        self.lugares_vip_coords = lugares_dict
        self.lista_lugares_visibles = sorted(list(self.lugares_vip_coords.keys()))
        
        self.ruta_actual = []
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        
        self.modo_marcado = tk.StringVar(value="origen") 
        self.modo_transporte = tk.StringVar(value="caminar") 

        self.root.title("EasyRoute - Navegación")
        self.root.geometry("1000x750")
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

        # Panel Izquierdo
        self.frame_controles = ttk.Frame(self.root, width=250, padding="10")
        self.frame_controles.pack(side="left", fill="y")
        
        ttk.Label(self.frame_controles, text="EasyRoute", font=("Helvetica", 20, "bold")).pack(pady=10)

        labelframe_marcado = ttk.LabelFrame(self.frame_controles, text="Herramienta de Marcado", padding=10)
        labelframe_marcado.pack(fill="x", pady=10)
        ttk.Radiobutton(labelframe_marcado, text="📍 Fijar Origen", variable=self.modo_marcado, value="origen").pack(anchor="w")
        ttk.Radiobutton(labelframe_marcado, text="🏁 Fijar Destino", variable=self.modo_marcado, value="destino").pack(anchor="w")

        ttk.Label(self.frame_controles, text="Origen:").pack(anchor="w", pady=(10,0))
        self.combo_origen = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_origen.pack(pady=5, fill="x")
        self.combo_origen.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("origen"))

        ttk.Label(self.frame_controles, text="Destino:").pack(anchor="w")
        self.combo_destino = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_destino.pack(pady=5, fill="x")
        self.combo_destino.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("destino"))
        
        ttk.Label(self.frame_controles, text="Modo de Transporte:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        frame_radios = ttk.Frame(self.frame_controles)
        frame_radios.pack(fill="x", padx=10)
        ttk.Radiobutton(frame_radios, text="🚶 Caminar (5 km/h)", variable=self.modo_transporte, value="caminar").pack(anchor="w")
        ttk.Radiobutton(frame_radios, text="🚗 Auto (40 km/h)", variable=self.modo_transporte, value="auto").pack(anchor="w")

        self.btn_buscar = ttk.Button(self.frame_controles, text="Calcular Ruta", command=self.buscar_ruta_presionado)
        self.btn_buscar.pack(pady=20, fill="x")
        ttk.Button(self.frame_controles, text="Limpiar Todo", command=self.limpiar_todo).pack(pady=5, fill="x")

        self.lbl_resultado = ttk.Label(self.frame_controles, text="Listo.", wraplength=230)
        self.lbl_resultado.pack(fill="x")

        self.frame_mapa = ttk.Frame(self.root)
        self.frame_mapa.pack(side="right", fill="both", expand=True)
        self.canvas_mapa = tk.Canvas(self.frame_mapa, bg="#333333") 
        self.canvas_mapa.pack(fill="both", expand=True)
        
        # --- EVENTOS ---
        self.canvas_mapa.bind('<Configure>', self.actualizar_mapa)
        
        # Clic IZQUIERDO: Navegación (Usuario normal)
        self.canvas_mapa.bind('<Button-1>', self.manejar_clic_mapa)
        
        # Clic DERECHO: Utilidad de Desarrollo
        # self.canvas_mapa.bind('<Button-3>', self.al_hacer_clic_derecho)


    # --- MÉTODO PARA CLIC DERECHO ---
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
        
    #     if coords:
    #         # Dibujamos un punto MAGENTA temporal donde hiciste clic derecho
    #         rx, ry = coords
    #         # Convertimos de nuevo a pantalla solo para dibujar
    #         fx = (rx * self.factor_escala) + self.offset_x
    #         fy = (ry * self.factor_escala) + self.offset_y
            
    #         self.canvas_mapa.delete("debug_point") # Borra el anterior
    #         self.canvas_mapa.create_oval(fx-3, fy-3, fx+3, fy+3, fill="magenta", outline="white", tags="debug_point")

    def formatear_nombre_visual(self, nombre_interno):
        if nombre_interno in self.lugares_vip_coords: return nombre_interno
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
        self.lbl_resultado.config(text="")
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
        METROS_POR_PIXEL = 2.5 
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
                msg = "⛔ Auto prohibido en Parque.\nSelecciona 'Caminar'."
            else:
                msg = "❌ Ruta no encontrada."
            self.lbl_resultado.config(text=msg)
            self.ruta_actual = []
        else:
            self.ruta_actual = ruta
            metros_reales = self.calcular_distancia_total(ruta)
            mins = int(tiempo_minutos)
            segs = int((tiempo_minutos - mins) * 60)
            
            if metros_reales >= 1000: texto_dist = f"{metros_reales/1000:.2f} km"
            else: texto_dist = f"{int(metros_reales)} m"

            self.lbl_resultado.config(text=f"✅ RUTA ENCONTRADA\n\n⏱ Tiempo: {mins} min {segs} s\n📏 Distancia: {texto_dist}\n🚗 Modo: {modo.upper()}")
        
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

        for n, (bx, by) in self.lugares_vip_coords.items():
            fx, fy = (bx*self.factor_escala)+self.offset_x, (by*self.factor_escala)+self.offset_y
            self.canvas_mapa.create_oval(fx-4, fy-4, fx+4, fy+4, fill="#FF9500", outline="white", width=2)

        if self.ruta_actual and len(self.ruta_actual) > 1:
            coords = []
            for nodo in self.ruta_actual:
                raw_x, raw_y = self.mapa.obtener_coordenadas(nodo)
                coords.extend([(raw_x*self.factor_escala)+self.offset_x, (raw_y*self.factor_escala)+self.offset_y])
            self.canvas_mapa.create_line(*coords, fill="#007AFF", width=5, arrow=tk.LAST, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        if self.nodo_origen_clic:
            ox, oy = self.mapa.obtener_coordenadas(self.nodo_origen_clic)
            self.dibujar_pin((ox*self.factor_escala)+self.offset_x, (oy*self.factor_escala)+self.offset_y, "green", "A")
        if self.nodo_destino_clic:
            dx, dy = self.mapa.obtener_coordenadas(self.nodo_destino_clic)
            self.dibujar_pin((dx*self.factor_escala)+self.offset_x, (dy*self.factor_escala)+self.offset_y, "red", "B")

    def dibujar_pin(self, x, y, c, t):
        self.canvas_mapa.create_line(x, y, x, y-20, width=2, fill=c)
        self.canvas_mapa.create_oval(x-10, y-30, x+10, y-10, fill=c, outline="white")
        self.canvas_mapa.create_text(x, y-20, text=t, fill="white", font=("Arial", 8, "bold"))