import tkinter as tk
import math
from Grafo import Grafo
from Interfaz import AppEasyRoute
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa con restricciones de tráfico ---")
    
    # Escala: 0.4 metros por píxel (Ajustable)
    METROS_POR_PIXEL = 0.4 
    
    todos_los_nodos = []

    # ==========================================
    # 1. CARGAR CALLES (DEFINIR SI ES PEATONAL O AUTO)
    # ==========================================
    for nombre_grupo, lista_coords in COORDENADAS_CALLES.items():
        
        # --- CAMBIO 1: LISTA DE PALABRAS PROHIBIDAS PARA AUTOS ---
        # Agregamos "Lago" y "Acceso" para que el auto no entre ahí.
        es_zona_verde = ("Parque" in nombre_grupo or 
                         "Picnic" in nombre_grupo or 
                         "Lago"   in nombre_grupo or 
                         "Acceso" in nombre_grupo)
                         
        tipo_via = "peatonal" if es_zona_verde else "universal"

        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_grupo}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_grupo})

        # Conectar nodos internos usando distancia real
        for i in range(len(nodos_calle) - 1):
            x1, y1 = lista_coords[i]
            x2, y2 = lista_coords[i+1]
            
            dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            dist_metros = dist_px * METROS_POR_PIXEL
            
            mapa.agregar_arista_doble_sentido(nodos_calle[i], nodos_calle[i+1], peso=dist_metros, tipo=tipo_via)

    # ==========================================
    # 2. CARGAR LUGARES VIP
    # ==========================================
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "LUGAR_VIP"})

    # ==========================================
    # 3. CONEXIÓN INTELIGENTE (CRUCES Y CORTAFUEGOS)
    # ==========================================
    print("--- Calculando intersecciones ---")
    
    UMBRAL_CALLES_PX = 40   
    UMBRAL_LUGARES_PX = 80  

    count_conexiones = 0

    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            grupo_a = nodo_a["grupo"]
            grupo_b = nodo_b["grupo"]
            es_vip_a = grupo_a == "LUGAR_VIP"
            es_vip_b = grupo_b == "LUGAR_VIP"

            if grupo_a == grupo_b and not es_vip_a: continue

            # --- CAMBIO 2: ACTUALIZAR EL CORTAFUEGOS ---
            # Definimos qué grupos son "Internos" del parque para protegerlos
            # Ahora incluye Lago y Acceso.
            def es_zona_protegida(grupo):
                return ("Parque" in grupo or "Picnic" in grupo or "Lago" in grupo or "Acceso" in grupo)

            es_calle_a = "Calle" in grupo_a or "Av_" in grupo_a or "Pasaje" in grupo_a
            es_calle_b = "Calle" in grupo_b or "Av_" in grupo_b or "Pasaje" in grupo_b
            
            es_interno_a = es_zona_protegida(grupo_a) and not es_vip_a
            es_interno_b = es_zona_protegida(grupo_b) and not es_vip_b

            # Si intentamos conectar Calle <-> Zona Protegida directamente: BLOQUEAR
            if (es_calle_a and es_interno_b) or (es_calle_b and es_interno_a):
                continue 
            # -----------------------------------------------------------

            # Radio dinámico
            radio_limite = UMBRAL_LUGARES_PX if (es_vip_a or es_vip_b) else UMBRAL_CALLES_PX
            dist_px = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            if dist_px < radio_limite:
                dist_metros = dist_px * METROS_POR_PIXEL
                
                # Penalización para evitar zigzag en edificios
                es_acceso_edificio = (es_vip_a or es_vip_b)
                # Sumamos 150 metros virtuales si entramos a un edificio para que no lo use de atajo
                peso_final = dist_metros + (150 if es_acceso_edificio else 0)

                mapa.agregar_arista_doble_sentido(nodo_a["nombre"], nodo_b["nombre"], peso=peso_final, tipo="universal")
                count_conexiones += 1
    
    print(f"--- Mapa listo: {count_conexiones} intersecciones calculadas ---")
    return mapa

if __name__ == "__main__":
    mi_mapa = cargar_mapa()
    root = tk.Tk()
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    root.mainloop()