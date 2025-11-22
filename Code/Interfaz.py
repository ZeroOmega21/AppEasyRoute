import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import os

class AppEasyRoute:
    def __init__(self, root, mapa, lugares_dict):
        self.root = root
        self.mapa = mapa 
        
        # Lugares VIP para el menú
        self.lugares_vip_coords = lugares_dict
        self.lista_lugares_visibles = sorted(list(self.lugares_vip_coords.keys()))
        
        # --- VARIABLES DE ESTADO ---
        self.ruta_actual = []
        self.costo_actual = 0
        
        # Variables para los clics en el mapa
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        self.modo_seleccion = "origen" # Alternará entre "origen" y "destino"

        self.root.title("EasyRoute - Navegación Interactiva")
        self.root.geometry("1000x700")

        self.factor_escala = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # --- 1. Carga de Imagen ---
        ruta_imagen = os.path.join("img", "Mapa.png")
        try:
            self.img_original = Image.open(ruta_imagen)
            self.ancho_base, self.alto_base = self.img_original.size
        except Exception as e:
            print(f"Error: {e}")
            self.img_original = Image.new("RGB", (800, 600), "white")
            self.ancho_base, self.alto_base = (800, 600)

        # --- 2. Controles ---
        self.frame_controles = ttk.Frame(self.root, width=250, padding="10")
        self.frame_controles.pack(side="left", fill="y")
        
        ttk.Label(self.frame_controles, text="EasyRoute", font=("Helvetica", 20, "bold")).pack(pady=10)

        # Instrucción
        self.lbl_instruccion = ttk.Label(self.frame_controles, text="Haz clic en el mapa para fijar el Origen", foreground="blue", wraplength=230)
        self.lbl_instruccion.pack(pady=10)

        # Menús (Ahora son opcionales si usas el mapa)
        ttk.Label(self.frame_controles, text="📍 Origen:").pack(anchor="w")
        self.combo_origen = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_origen.pack(pady=5, fill="x")
        # Evento: Si selecciona del menú, limpiamos el clic manual
        self.combo_origen.bind("<<ComboboxSelected>>", lambda e: self.resetear_clic("origen"))

        ttk.Label(self.frame_controles, text="🏁 Destino:").pack(anchor="w")
        self.combo_destino = ttk.Combobox(self.frame_controles, values=self.lista_lugares_visibles, state="readonly")
        self.combo_destino.pack(pady=5, fill="x")
        self.combo_destino.bind("<<ComboboxSelected>>", lambda e: self.resetear_clic("destino"))
        
        self.btn_buscar = ttk.Button(self.frame_controles, text="Calcular Ruta", command=self.buscar_ruta_presionado)
        self.btn_buscar.pack(pady=20, fill="x")
        
        # Botón para limpiar
        ttk.Button(self.frame_controles, text="Limpiar Mapa", command=self.limpiar_todo).pack(pady=5, fill="x")

        self.lbl_resultado = ttk.Label(self.frame_controles, text="Esperando...", wraplength=230)
        self.lbl_resultado.pack(fill="x")

        # --- 3. Mapa ---
        self.frame_mapa = ttk.Frame(self.root)
        self.frame_mapa.pack(side="right", fill="both", expand=True)

        self.canvas_mapa = tk.Canvas(self.frame_mapa, bg="#333333") 
        self.canvas_mapa.pack(fill="both", expand=True)

        self.canvas_mapa.bind('<Configure>', self.actualizar_mapa)
        
        # CAMBIO: Ahora el clic llama a la función de navegación
        self.canvas_mapa.bind('<Button-1>', self.manejar_clic_mapa)

    def resetear_clic(self, tipo):
        """Si el usuario elige del menú, borramos el marcador manual correspondiente"""
        if tipo == "origen":
            self.nodo_origen_clic = None
        elif tipo == "destino":
            self.nodo_destino_clic = None
        self.redibujar_todo()

    def limpiar_todo(self):
        self.nodo_origen_clic = None
        self.nodo_destino_clic = None
        self.ruta_actual = []
        self.combo_origen.set('')
        self.combo_destino.set('')
        self.modo_seleccion = "origen"
        self.lbl_instruccion.config(text="Haz clic para fijar Origen", foreground="blue")
        self.redibujar_todo()

    def actualizar_mapa(self, event):
        ancho_canvas = event.width
        alto_canvas = event.height
        if ancho_canvas < 10: return

        # Escalar imagen
        ratio = min(ancho_canvas / self.ancho_base, alto_canvas / self.alto_base)
        self.factor_escala = ratio

        nw = int(self.ancho_base * ratio)
        nh = int(self.alto_base * ratio)
        self.offset_x = (ancho_canvas - nw) // 2
        self.offset_y = (alto_canvas - nh) // 2

        img_ajustada = self.img_original.resize((nw, nh), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img_ajustada)

        self.redibujar_todo()

    def redibujar_todo(self):
        """Redibuja capas: Fondo -> Puntos VIP -> Ruta -> Marcadores Manuales"""
        self.canvas_mapa.delete("all")
        
        # 1. Fondo
        self.canvas_mapa.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.img_tk)

        # 2. Lugares VIP (Naranjas)
        for nombre, (bx, by) in self.lugares_vip_coords.items():
            fx, fy = self.transformar_coords(bx, by)
            self.dibujar_punto(fx, fy, "#FF9500", 4)

        # 3. Ruta
        if self.ruta_actual:
            self.dibujar_ruta()

        # 4. Marcadores de Clic (Origen = Verde, Destino = Rojo)
        if self.nodo_origen_clic:
            ox, oy = self.mapa.obtener_coordenadas(self.nodo_origen_clic)
            fx, fy = self.transformar_coords(ox, oy)
            self.dibujar_pin(fx, fy, "green", "A")
        
        if self.nodo_destino_clic:
            dx, dy = self.mapa.obtener_coordenadas(self.nodo_destino_clic)
            fx, fy = self.transformar_coords(dx, dy)
            self.dibujar_pin(fx, fy, "red", "B")

    def manejar_clic_mapa(self, event):
        # 1. Obtener coordenada real en el mapa (Matemática inversa)
        try:
            real_x = int((event.x - self.offset_x) / self.factor_escala)
            real_y = int((event.y - self.offset_y) / self.factor_escala)
        except ZeroDivisionError:
            return

        # 2. Buscar el nodo (calle) más cercano al clic
        # (Requiere que hayas actualizado Grafo.py en el paso anterior)
        nodo_cercano, dist = self.mapa.obtener_nodo_mas_cercano(real_x, real_y)

        if not nodo_cercano: return

        # 3. Asignar según el turno
        if self.modo_seleccion == "origen":
            self.nodo_origen_clic = nodo_cercano
            self.combo_origen.set(f"📍 {nodo_cercano}") # Mostramos visualmente
            
            self.modo_seleccion = "destino"
            self.lbl_instruccion.config(text="Ahora haz clic para fijar el Destino", foreground="red")
        
        else: # modo destino
            self.nodo_destino_clic = nodo_cercano
            self.combo_destino.set(f"🏁 {nodo_cercano}")
            
            self.modo_seleccion = "origen" # Volvemos a empezar para la próxima
            self.lbl_instruccion.config(text="¡Listo! Pulsa 'Calcular Ruta'", foreground="green")
            
            # Opcional: Calcular automáticamente al poner el segundo punto
            self.buscar_ruta_presionado()

        self.redibujar_todo()

    def buscar_ruta_presionado(self):
        # Prioridad: Si hay clic manual, usamos ese. Si no, usamos el Combobox
        origen = self.nodo_origen_clic if self.nodo_origen_clic else self.combo_origen.get()
        destino = self.nodo_destino_clic if self.nodo_destino_clic else self.combo_destino.get()

        # Limpieza de strings por si vienen del combobox (quitamos emojis si los hubiera)
        # Pero como tus nombres de diccionario no tienen emojis, funcionará directo si seleccionan del combo.

        if not origen or not destino:
            messagebox.showwarning("Atención", "Faltan puntos de origen o destino.")
            return
        
        # Dijkstra
        ruta, costo = self.mapa.dijkstra(origen, destino)

        if not ruta:
            self.lbl_resultado.config(text=f"❌ No hay camino.")
            self.ruta_actual = []
            self.redibujar_todo()
            return

        self.ruta_actual = ruta
        texto_ruta = " ➝ ".join(ruta)
        if len(ruta) > 4: texto_ruta = f"{ruta[0]} ... ({len(ruta)} pasos) ... {ruta[-1]}"
        
        self.lbl_resultado.config(text=f"✅ Ruta ({costo} px aprox):\n{texto_ruta}")
        self.redibujar_todo()

    # --- Ayudantes Gráficos ---
    def transformar_coords(self, x, y):
        return (x * self.factor_escala) + self.offset_x, (y * self.factor_escala) + self.offset_y

    def dibujar_punto(self, x, y, color, r):
        self.canvas_mapa.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="white", width=2)

    def dibujar_pin(self, x, y, color, letra):
        # Dibuja un marcador tipo Google Maps
        self.canvas_mapa.create_line(x, y, x, y-20, width=2, fill=color)
        self.canvas_mapa.create_oval(x-10, y-30, x+10, y-10, fill=color, outline="white")
        self.canvas_mapa.create_text(x, y-20, text=letra, fill="white", font=("Arial", 8, "bold"))

    def dibujar_ruta(self):
        for i in range(len(self.ruta_actual) - 1):
            na, nb = self.ruta_actual[i], self.ruta_actual[i+1]
            xa, ya = self.mapa.obtener_coordenadas(na)
            xb, yb = self.mapa.obtener_coordenadas(nb)
            
            x1, y1 = self.transformar_coords(xa, ya)
            x2, y2 = self.transformar_coords(xb, yb)
            
            self.canvas_mapa.create_line(x1, y1, x2, y2, fill="#007AFF", width=5, arrow=tk.LAST, capstyle=tk.ROUND)