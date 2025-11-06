# --- archivo: main.py ---

import tkinter as tk
from Grafo import Grafo      # Importamos el motor del Grafo
from Interfaz import AppEasyRoute   # Importamos nuestra nueva clase de Interfaz

def cargar_mapa():
    """
    Esta función sigue siendo la misma:
    Construye nuestro objeto Grafo con todos los nodos y aristas.
    """
    print("--- Creando instancia del mapa 'EasyRoute' ---")
    mapa = Grafo()

    # --- INICIO DE TU TAREA: Digitalizar el mapa ---
    # (Aquí va todo tu código de 'mapa.agregar_nodo' y 'mapa.agregar_arista')
    # ...
    mapa.agregar_nodo("Hospital Urgencia")
    mapa.agregar_nodo("El Templo del Smash")
    mapa.agregar_nodo("SmartFit Portugal")
    mapa.agregar_nodo("Supermercado Tottus")
    mapa.agregar_nodo("Universidad Silva Henriquez")
    
    mapa.agregar_nodo("Interseccion_Diag_Curico")
    mapa.agregar_nodo("Interseccion_Diag_SantaIsabel")
    mapa.agregar_nodo("Interseccion_Portugal_Curico")
    mapa.agregar_nodo("Interseccion_Lira_Curico")

    mapa.agregar_arista_doble_sentido("Hospital Urgencia", "Interseccion_Diag_Curico", 50)
    mapa.agregar_arista_doble_sentido("Hospital Urgencia", "Interseccion_Diag_SantaIsabel", 200)
    mapa.agregar_arista_doble_sentido("El Templo del Smash", "Interseccion_Diag_Curico", 150)
    mapa.agregar_arista_doble_sentido("El Templo del Smash", "Interseccion_Portugal_Curico", 100)
    mapa.agregar_arista_doble_sentido("Interseccion_Portugal_Curico", "Interseccion_Diag_Curico", 120)
    mapa.agregar_arista_doble_sentido("Interseccion_Portugal_Curico", "Interseccion_Lira_Curico", 100)
    mapa.agregar_arista_doble_sentido("SmartFit Portugal", "Interseccion_Portugal_Curico", 30)
    # ...
    # --- FIN DE TU TAREA ---
    
    print("--- Mapa cargado con éxito ---")
    return mapa

# --- PUNTO DE INICIO DEL PROGRAMA ---
if __name__ == "__main__":
    
    # 1. Construimos el mapa en memoria
    mi_mapa_easyroute = cargar_mapa()

    # 2. Creamos la ventana principal de la aplicación
    root = tk.Tk()
    
    # 3. Creamos una instancia de nuestra App, pasándole la ventana (root)
    #    y el objeto 'mi_mapa_easyroute' que contiene nuestro grafo.
    app = AppEasyRoute(root, mapa=mi_mapa_easyroute)

    # 4. Iniciamos el bucle principal de tkinter (esto mantiene la ventana abierta)
    root.mainloop()