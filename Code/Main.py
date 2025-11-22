import tkinter as tk
import math
from Grafo import Grafo
from Interfaz import AppEasyRoute
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa con zonas de tráfico ---")
    
    todos_los_nodos = []

    # 1. CARGAR CALLES Y DEFINIR ZONAS (PEATONAL VS UNIVERSAL)
    for nombre_grupo, lista_coords in COORDENADAS_CALLES.items():
        
        # Detectar si es zona verde (Parque/Picnic)
        es_zona_verde = "Parque" in nombre_grupo or "Picnic" in nombre_grupo
        tipo_via = "peatonal" if es_zona_verde else "universal"

        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_grupo}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_grupo})

        # Conectar nodos internos de la calle
        for i in range(len(nodos_calle) - 1):
            mapa.agregar_arista_doble_sentido(nodos_calle[i], nodos_calle[i+1], peso=10, tipo=tipo_via)

    # 2. CARGAR LUGARES VIP (Lugares de Interés)
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        # Los marcamos como grupo 'LUGAR_VIP'
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "LUGAR_VIP"})

    # 3. CONEXIÓN AUTOMÁTICA INTELIGENTE (Opción B)
    print("--- Conectando cruces y accesos ---")
    
    # Radio pequeño para calles (evita saltos de vereda)
    UMBRAL_CALLES = 35 
    # Radio grande para lugares (facilita el acceso)
    UMBRAL_LUGARES = 80 

    count_conexiones = 0

    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            # Regla 1: No conectar nodos del mismo grupo (ej: Calle1_0 con Calle1_5)
            # EXCEPTO si uno es VIP (queremos que se conecte a todo lo cercano)
            if nodo_a["grupo"] == nodo_b["grupo"] and nodo_a["grupo"] != "LUGAR_VIP":
                continue

            # Regla 2: Decidir qué radio usar (Dinámico)
            es_vip = (nodo_a["grupo"] == "LUGAR_VIP" or nodo_b["grupo"] == "LUGAR_VIP")
            radio_limite = UMBRAL_LUGARES if es_vip else UMBRAL_CALLES

            # Cálculo de distancia
            distancia = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            # Regla 3: Si está dentro del radio, conectar
            if distancia < radio_limite:
                # Las conexiones de acceso son universales
                mapa.agregar_arista_doble_sentido(nodo_a["nombre"], nodo_b["nombre"], peso=5, tipo="universal")
                count_conexiones += 1
    
    print(f"--- Mapa listo: {count_conexiones} conexiones generadas ---")
    return mapa

if __name__ == "__main__":
    mi_mapa = cargar_mapa()
    root = tk.Tk()
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    root.mainloop()