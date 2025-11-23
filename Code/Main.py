import tkinter as tk
import math
from Grafo import Grafo
from Interfaz import AppEasyRoute
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa con zonas de tráfico ---")
    
    todos_los_nodos = []

    # ==========================================
    # 1. CARGAR CALLES Y DEFINIR ZONAS
    # ==========================================
    for nombre_grupo, lista_coords in COORDENADAS_CALLES.items():
        
        # Detectar si es zona verde (Parque/Picnic) para prohibir autos
        es_zona_verde = "Parque" in nombre_grupo or "Picnic" in nombre_grupo
        tipo_via = "peatonal" if es_zona_verde else "universal"

        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_grupo}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            
            # Guardamos info para la conexión automática
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_grupo})

        # Conectar nodos internos de la calle consigo misma
        for i in range(len(nodos_calle) - 1):
            mapa.agregar_arista_doble_sentido(nodos_calle[i], nodos_calle[i+1], peso=10, tipo=tipo_via)

    # ==========================================
    # 2. CARGAR LUGARES VIP (Puntos Naranjas)
    # ==========================================
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        # Los marcamos con un grupo especial 'LUGAR_VIP'
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "LUGAR_VIP"})

    # ==========================================
    # 3. CONEXIÓN AUTOMÁTICA INTELIGENTE
    # ==========================================
    print("--- Conectando cruces y accesos ---")
    
    UMBRAL_CALLES = 40   # Radio pequeño para calles (evita saltos de vereda)
    UMBRAL_LUGARES = 80  # Radio grande para que las Entradas alcancen la calle

    count_conexiones = 0

    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            grupo_a = nodo_a["grupo"]
            grupo_b = nodo_b["grupo"]
            
            es_vip_a = grupo_a == "LUGAR_VIP"
            es_vip_b = grupo_b == "LUGAR_VIP"

            # Regla 0: No conectar nodos del mismo grupo (salvo VIPs)
            if grupo_a == grupo_b and not es_vip_a:
                continue

            # --- REGLA DE CORTAFUEGOS (PARQUE) ---
            es_calle_a = "Calle" in grupo_a
            es_calle_b = "Calle" in grupo_b
            es_parque_interno_a = ("Parque" in grupo_a or "Picnic" in grupo_a) and not es_vip_a
            es_parque_interno_b = ("Parque" in grupo_b or "Picnic" in grupo_b) and not es_vip_b

            # Si intentamos conectar una Calle directamente con el interior del Parque: PROHIBIDO
            if (es_calle_a and es_parque_interno_b) or (es_calle_b and es_parque_interno_a):
                continue 

            # Definir el radio de búsqueda
            radio_limite = UMBRAL_LUGARES if (es_vip_a or es_vip_b) else UMBRAL_CALLES

            # Cálculo de distancia
            distancia = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            if distancia < radio_limite:
                
                # --- CORRECCIÓN ANTI-ZIGZAG (SOLUCIÓN) ---
                # Si estamos conectando con un lugar VIP (Edificio/Acceso), ponemos un peso MUY ALTO (50).
                # Si es un cruce de calles normal, peso BAJO (5).
                es_acceso_edificio = (es_vip_a or es_vip_b)
                peso_conexion = 50 if es_acceso_edificio else 5

                mapa.agregar_arista_doble_sentido(
                    nodo_a["nombre"], 
                    nodo_b["nombre"], 
                    peso=peso_conexion, 
                    tipo="universal"
                )
                count_conexiones += 1
    
    print(f"--- Mapa listo: {count_conexiones} conexiones generadas ---")
    return mapa

if __name__ == "__main__":
    mi_mapa = cargar_mapa()
    root = tk.Tk()
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    root.mainloop()