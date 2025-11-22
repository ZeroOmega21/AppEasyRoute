import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os

class AppEasyRoute:
    def __init__(self, root, mapa, lugares_dict):
        self.root = root
        self.mapa = mapa 
        self.lugares_vip_coords = lugares_dict
        self.lista_lugares_visibles = sorted(list(self.lugares_vip_coords.keys()))
        
        # Variables de Estado
        self.ruta_actual = []
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        
        # --- NUEVO: VARIABLE PARA CONTROLAR QUÉ MARCAMOS CON EL CLIC ---
        # Valores posibles: "origen" o "destino"
        self.modo_marcado = tk.StringVar(value="origen") 
        
        # Variable para auto/caminar
        self.modo_transporte = tk.StringVar(value="caminar") 

        self.root.title("EasyRoute - Navegación")
        self.root.geometry("1000x750") # Un poco más alto para que quepan los botones
        self.factor_escala = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # --- Carga Imagen ---
        try:
            self.img_original = Image.open(os.path.join("img", "Mapa.png"))
            self.ancho_base, self.alto_base = self.img_original.size
        except:
            self.img_original = Image.new("RGB", (800, 600), "white")
            self.ancho_base, self.alto_base = (800, 600)

        # --- Panel Izquierdo ---
        self.frame_controles = ttk.Frame(self.root, width=250, padding="10")
        self.frame_controles.pack(side="left", fill="y")
        
        ttk.Label(self.frame_controles, text="EasyRoute", font=("Helvetica", 20, "bold")).pack(pady=10)

        # --- SECCIÓN 1: QUÉ QUIERES MARCAR ---
        # Aquí eliges si tu próximo clic será el punto A o el punto B
        labelframe_marcado = ttk.LabelFrame(self.frame_controles, text="¿Qué deseas marcar?", padding=10)
        labelframe_marcado.pack(fill="x", pady=10)
        
        ttk.Radiobutton(labelframe_marcado, text="📍 Fijar Origen", variable=self.modo_marcado, value="origen").pack(anchor="w", pady=2)
        ttk.Radiobutton(labelframe_marcado, text="🏁 Fijar Destino", variable=self.modo_marcado, value="destino").pack(anchor="w", pady=2)

        # --- SECCIÓN 2: SELECCIÓN Y TEXTO ---
        ttk.Label(self.frame_controles, text="Ubicación Origen:").pack(anchor="w", pady=(10,0))
        self.combo_origen = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_origen.pack(pady=5, fill="x")
        # Si seleccionan del menú, borramos el pin manual
        self.combo_origen.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("origen"))

        ttk.Label(self.frame_controles, text="Ubicación Destino:").pack(anchor="w")
        self.combo_destino = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_destino.pack(pady=5, fill="x")
        self.combo_destino.bind("<<ComboboxSelected>>", lambda e: self.resetear_pin_manual("destino"))
        
        # --- SECCIÓN 3: MODO TRANSPORTE ---
        ttk.Label(self.frame_controles, text="Modo de Transporte:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        frame_radios = ttk.Frame(self.frame_controles)
        frame_radios.pack(fill="x", padx=10)
        ttk.Radiobutton(frame_radios, text="🚶 Caminar", variable=self.modo_transporte, value="caminar").pack(anchor="w")
        ttk.Radiobutton(frame_radios, text="🚗 Auto", variable=self.modo_transporte, value="auto").pack(anchor="w")

        # Botones Acción
        self.btn_buscar = ttk.Button(self.frame_controles, text="Calcular Ruta", command=self.buscar_ruta_presionado)
        self.btn_buscar.pack(pady=20, fill="x")
        ttk.Button(self.frame_controles, text="Limpiar Todo", command=self.limpiar_todo).pack(pady=5, fill="x")

        self.lbl_resultado = ttk.Label(self.frame_controles, text="Selecciona modo y haz clic en el mapa.", wraplength=230)
        self.lbl_resultado.pack(fill="x")

        # --- Mapa ---
        self.frame_mapa = ttk.Frame(self.root)
        self.frame_mapa.pack(side="right", fill="both", expand=True)
        self.canvas_mapa = tk.Canvas(self.frame_mapa, bg="#333333") 
        self.canvas_mapa.pack(fill="both", expand=True)
        
        self.canvas_mapa.bind('<Configure>', self.actualizar_mapa)
        self.canvas_mapa.bind('<Button-1>', self.manejar_clic_mapa)

    def resetear_pin_manual(self, tipo):
        """Si eligen del menú desplegable, quitamos el pin manual del mapa"""
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
        """
        Este método ahora obedece a lo que hayas seleccionado en los RadioButtons
        """
        try:
            rx = int((event.x - self.offset_x) / self.factor_escala)
            ry = int((event.y - self.offset_y) / self.factor_escala)
        except: return

        # 1. Buscar nodo cercano
        nodo, dist = self.mapa.obtener_nodo_mas_cercano(rx, ry)
        if not nodo: return

        # 2. VERIFICAR QUÉ ESTAMOS MARCANDO (Origen o Destino)
        accion = self.modo_marcado.get()

        if accion == "origen":
            self.nodo_origen_clic = nodo
            self.combo_origen.set(f"📍 {nodo}")
            # Opcional: Cambiar automáticamente al siguiente modo para agilizar
            # self.modo_marcado.set("destino") 
        
        elif accion == "destino":
            self.nodo_destino_clic = nodo
            self.combo_destino.set(f"🏁 {nodo}")

        # Redibujamos para que aparezca el pin (Verde o Rojo)
        self.redibujar_todo()

        # Si ya tenemos los dos, calculamos ruta automáticamente (opcional)
        origen = self.nodo_origen_clic if self.nodo_origen_clic else self.combo_origen.get()
        destino = self.nodo_destino_clic if self.nodo_destino_clic else self.combo_destino.get()
        
        if origen and destino:
             self.buscar_ruta_presionado()


    def buscar_ruta_presionado(self):
        origen = self.nodo_origen_clic if self.nodo_origen_clic else self.combo_origen.get()
        destino = self.nodo_destino_clic if self.nodo_destino_clic else self.combo_destino.get()
        
        if not origen or not destino:
            return # No mostramos error, solo esperamos
        
        modo = self.modo_transporte.get()
        ruta, costo = self.mapa.dijkstra(origen, destino, modo_transporte=modo)

        if not ruta:
            if modo == "auto" and ("Parque" in destino or "Picnic" in destino):
                msg = "⛔ Auto prohibido en Parque."
            else:
                msg = "❌ Ruta no encontrada."
            self.lbl_resultado.config(text=msg)
            self.ruta_actual = []
        else:
            self.ruta_actual = ruta
            texto_resumen = " ➝ ".join(ruta)
            if len(ruta) > 4: texto_resumen = f"Inicio... ({len(ruta)} pasos) ... Fin"
            self.lbl_resultado.config(text=f"✅ Ruta {modo.upper()} ({costo:.0f}):\n{texto_resumen}")
        
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

        # Puntos VIP
        for n, (bx, by) in self.lugares_vip_coords.items():
            fx, fy = (bx*self.factor_escala)+self.offset_x, (by*self.factor_escala)+self.offset_y
            self.canvas_mapa.create_oval(fx-4, fy-4, fx+4, fy+4, fill="#FF9500", outline="white", width=2)

        # Ruta Suave
        if self.ruta_actual and len(self.ruta_actual) > 1:
            coordenadas_ruta = []
            for nodo in self.ruta_actual:
                raw_x, raw_y = self.mapa.obtener_coordenadas(nodo)
                final_x = (raw_x * self.factor_escala) + self.offset_x
                final_y = (raw_y * self.factor_escala) + self.offset_y
                coordenadas_ruta.extend([final_x, final_y])
            
            self.canvas_mapa.create_line(
                *coordenadas_ruta, 
                fill="#007AFF", width=5, arrow=tk.LAST, 
                capstyle=tk.ROUND, joinstyle=tk.ROUND
            )

        # Pines de clic
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