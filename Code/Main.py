import tkinter as tk
from Grafo import Grafo
from Interfaz import AppEasyRoute

# Importamos Datos
from datos_mapa import COORDENADAS_CALLES, LUGARES_INTERES, DICCIONARIO_SENTIDOS

# Importamos Lógica desde Utilidades
from utilidades import conectar_tramos_con_sentido, conectar_cruces_inteligentes, es_zona_protegida

def cargar_mapa():
    mapa = Grafo()
    print("--- Generando mapa modularizado ---")
    
    METROS_POR_PIXEL = 0.5 
    todos_los_nodos = []

    # 1. CARGAR CALLES
    for nombre_grupo, lista_coords in COORDENADAS_CALLES.items():
        
        tipo_via = "peatonal" if es_zona_protegida(nombre_grupo) else "universal"

        nodos_calle = []
        for i, (x, y) in enumerate(lista_coords):
            nombre_nodo = f"{nombre_grupo}_{i}"
            mapa.agregar_nodo(nombre_nodo, x=x, y=y)
            nodos_calle.append(nombre_nodo)
            todos_los_nodos.append({"nombre": nombre_nodo, "x": x, "y": y, "grupo": nombre_grupo})

        conectar_tramos_con_sentido(
            mapa=mapa,
            nodos_calle=nodos_calle,
            coords_calle=lista_coords,
            nombre_calle=nombre_grupo,
            sentidos_dict=DICCIONARIO_SENTIDOS,
            tipo_via=tipo_via,
            escala_metros=METROS_POR_PIXEL
        )

    # 2. CARGAR PUNTOS DE INTERÉS
    for nombre_lugar, (x, y) in LUGARES_INTERES.items():
        mapa.agregar_nodo(nombre_lugar, x=x, y=y)
        # --- CAMBIO DE NOMBRE AQUÍ ---
        todos_los_nodos.append({"nombre": nombre_lugar, "x": x, "y": y, "grupo": "PUNTO_INTERES"})

    # 3. CONEXIÓN INTELIGENTE
    conectar_cruces_inteligentes(mapa, todos_los_nodos, METROS_POR_PIXEL)
    
    return mapa

if __name__ == "__main__":
    mi_mapa = cargar_mapa()
    root = tk.Tk()
    app = AppEasyRoute(root, mapa=mi_mapa, lugares_dict=LUGARES_INTERES)
    root.mainloop()