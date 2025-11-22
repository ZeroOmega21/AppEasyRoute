import tkinter as tk
import math
from Grafo import Grafo
from Interfaz import AppEasyRoute

# Importamos tus datos (Calles y Lugares VIP)
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa digitalizado ---")
    
    todos_los_nodos = []

    # 1. CARGAR CALLES (Red vial)
    # ------------------------------------------------
    for nombre_calle, lista_coords in COORDENADAS_CALLES.items():
        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_calle}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            
            # Guardamos info para la detección de cruces
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_calle})

        # Conectar la calle consigo misma secuencialmente
        for i in range(len(nodos_calle) - 1):
            mapa.agregar_arista_doble_sentido(nodos_calle[i], nodos_calle[i+1], peso=10)

    # 2. CARGAR LUGARES DE INTERÉS (Destinos VIP)
    # ------------------------------------------------
    print("--- Cargando lugares de interés ---")
    
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        # Agregamos el nodo al grafo para que Dijkstra pueda llegar a él
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        
        # Lo agregamos a la lista de comparación con grupo "LUGAR_VIP"
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "LUGAR_VIP"})

    # 3. CONEXIÓN AUTOMÁTICA (Auto-Intersección)
    # ------------------------------------------------
    print("--- Conectando calles y lugares ---")
    UMBRAL_CONEXION = 60 # Distancia en pixeles para unir puntos

    count_conexiones = 0
    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            # Regla: No conectar nodos de la misma calle (ya están unidos),
            # EXCEPTO si uno es un LUGAR_VIP (siempre queremos conectarlo a la calle)
            if nodo_a["grupo"] == nodo_b["grupo"] and nodo_a["grupo"] != "LUGAR_VIP":
                continue

            distancia = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            if distancia < UMBRAL_CONEXION:
                # print(f"[+] Conectado: {nodo_a['nombre']} <--> {nodo_b['nombre']}")
                mapa.agregar_arista_doble_sentido(nodo_a["nombre"], nodo_b["nombre"], peso=5)
                count_conexiones += 1
    
    print(f"--- Mapa listo con {count_conexiones} intersecciones automáticas ---")
    return mapa

if __name__ == "__main__":
    # 1. Cargamos la lógica del grafo
    mi_mapa = cargar_mapa()
    
    root = tk.Tk()
    
    # 2. Iniciamos la Interfaz
    # Pasamos 'LUGARES_INTERES' para que la interfaz sepa dónde dibujar los puntos naranjas
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    
    root.mainloop()