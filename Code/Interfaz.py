# --- archivo: interfaz.py ---

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Necesitamos Pillow para cargar JPGs

class AppEasyRoute:
    def __init__(self, root, mapa):
        """
        Constructor de la interfaz.
        - 'root' es la ventana principal de tkinter.
        - 'mapa' es la instancia de tu Grafo que creamos en main.py.
        """
        self.root = root
        self.mapa = mapa # Guardamos la referencia al grafo
        
        # --- Configuración de la Ventana ---
        self.root.title("EasyRoute - Buscador de Rutas")
        self.root.geometry("1000x800") # Ajusta el tamaño según necesites

        # --- 1. Frame de Controles (Izquierda) ---
        self.frame_controles = ttk.Frame(self.root, width=250, padding="10")
        self.frame_controles.pack(side="left", fill="y")
        
        ttk.Label(self.frame_controles, text="EasyRoute", font=("Helvetica", 20, "bold")).pack(pady=10)

        # Obtenemos la lista de nodos del mapa para los desplegables
        # Usamos list() para convertir las claves del diccionario en una lista
        lista_nodos = sorted(list(self.mapa.adj_list.keys()))

        # Desplegable de Origen
        ttk.Label(self.frame_controles, text="📍 Origen:").pack(padx=10, anchor="w")
        self.combo_origen = ttk.Combobox(self.frame_controles, values=lista_nodos, state="readonly", width=30)
        self.combo_origen.pack(padx=10, pady=5, fill="x")

        # Desplegable de Destino
        ttk.Label(self.frame_controles, text="🏁 Destino:").pack(padx=10, anchor="w")
        self.combo_destino = ttk.Combobox(self.frame_controles, values=lista_nodos, state="readonly", width=30)
        self.combo_destino.pack(padx=10, pady=5, fill="x")
        
        # Botón de Búsqueda
        self.btn_buscar = ttk.Button(self.frame_controles, text="Buscar Ruta Más Corta", command=self.buscar_ruta_presionado)
        self.btn_buscar.pack(pady=20, fill="x", padx=10)

        # Etiqueta para mostrar resultados
        ttk.Label(self.frame_controles, text="Resultado:").pack(padx=10, anchor="w", pady=10)
        self.lbl_resultado = ttk.Label(self.frame_controles, text="Selecciona origen y destino...", wraplength=230, font=("Helvetica", 10))
        self.lbl_resultado.pack(padx=10, fill="x")

        # --- 2. Frame del Mapa (Derecha) ---
        self.frame_mapa = ttk.Frame(self.root)
        self.frame_mapa.pack(side="right", fill="both", expand=True)

        # Creamos un Canvas para dibujar el mapa y las rutas
        self.canvas_mapa = tk.Canvas(self.frame_mapa, bg="white")
        self.canvas_mapa.pack(fill="both", expand=True)

        self.cargar_imagen_mapa()

    def cargar_imagen_mapa(self):
        """
        Carga la imagen 'Mapa.png' y la pone en el Canvas.
        """
        try:
            # Abrimos la imagen
            img_original = Image.open("img\Mapa.png")
            
            # (Opcional) Ajustamos el tamaño si es muy grande, por ahora la dejamos original
            # img_original = img_original.resize((750, 750), Image.LANCZOS)

            # Convertimos a formato de tkinter
            self.img_tk = ImageTk.PhotoImage(img_original)
            
            # La dibujamos en el canvas
            self.canvas_mapa.create_image(0, 0, anchor="nw", image=self.img_tk)
            
        except FileNotFoundError:
            self.canvas_mapa.create_text(300, 300, text="Error: No se encontró 'Mapa.png'", fill="red", font=("Helvetica", 12))
        except Exception as e:
            self.canvas_mapa.create_text(300, 300, text=f"Error al cargar imagen: {e}", fill="red", font=("Helvetica", 12))

    def buscar_ruta_presionado(self):
        """
        Esta función se llamará cuando el usuario presione el botón.
        """
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()

        if not origen or not destino:
            messagebox.showwarning("Error", "Debes seleccionar un origen y un destino.")
            return
            
        if origen == destino:
            messagebox.showinfo("Info", "El origen y el destino son el mismo.")
            self.lbl_resultado.config(text="El origen y el destino son el mismo.")
            return
            
        # --- ¡¡AQUÍ LLAMAREMOS A DIJKSTRA!! ---
        # Por ahora, ponemos un placeholder:
        print(f"Buscando ruta de {origen} a {destino}...")
        
        # --- Próximo paso: Implementar esto ---
        # ruta, costo = self.mapa.encontrar_ruta_mas_corta(origen, destino)
        
        # --- Simulación temporal ---
        self.lbl_resultado.config(text=f"Próximo paso:\nImplementar Dijkstra para encontrar la ruta de '{origen}' a '{destino}'.")