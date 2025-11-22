import tkinter as tk
import math
from Grafo import Grafo
from Interfaz import AppEasyRoute
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa con zonas de tráfico ---")
    
    todos_los_nodos = []

    # 1. CARGAR CALLES
    for nombre_grupo, lista_coords in COORDENADAS_CALLES.items():
        es_zona_verde = "Parque" in nombre_grupo or "Picnic" in nombre_grupo
        tipo_via = "peatonal" if es_zona_verde else "universal"

        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_grupo}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_grupo})

        for i in range(len(nodos_calle) - 1):
            mapa.agregar_arista_doble_sentido(nodos_calle[i], nodos_calle[i+1], peso=10, tipo=tipo_via)

    # 2. CARGAR LUGARES VIP
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "LUGAR_VIP"})

    # 3. CONEXIÓN AUTOMÁTICA
    print("--- Conectando cruces ---")
    
    # --- SOLUCIÓN AL PROBLEMA DE NODOS QUE SE TOPAN INDEBIDAMENTE ---
    # Bajamos el umbral de 60 a 35. 
    # Como tus puntos están muy seguidos, 60 era demasiado grande y saltaba veredas.
    UMBRAL_CONEXION = 35 

    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            if nodo_a["grupo"] == nodo_b["grupo"] and nodo_a["grupo"] != "LUGAR_VIP":
                continue

            distancia = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            if distancia < UMBRAL_CONEXION:
                mapa.agregar_arista_doble_sentido(nodo_a["nombre"], nodo_b["nombre"], peso=5, tipo="universal")
    
    return mapa

if __name__ == "__main__":
    mi_mapa = cargar_mapa()
    root = tk.Tk()
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    root.mainloop()