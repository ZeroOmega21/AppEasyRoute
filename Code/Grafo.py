# --- archivo: logica_rutas.py ---

import heapq

class Grafo:
    def __init__(self):
        self.adj_list = {}

    def agregar_nodo(self, nombre_nodo):
        if nombre_nodo not in self.adj_list:
            self.adj_list[nombre_nodo] = []
            print(f"Nodo '{nombre_nodo}' agregado.")

    def agregar_arista(self, origen, destino, peso):
        if origen not in self.adj_list:
            self.agregar_nodo(origen)
        if destino not in self.adj_list:
            self.agregar_nodo(destino)

        self.adj_list[origen].append((destino, peso))
        print(f"Arista agregada: {origen} -> {destino} (Peso: {peso})")

    # ¡¡AÑADE ESTE MÉTODO AQUÍ!!
    def agregar_arista_doble_sentido(self, nodo_a, nodo_b, peso):
        """
        Método de ayuda para calles de doble sentido.
        Llama a agregar_arista dos veces: una en cada dirección.
        """
        self.agregar_arista(nodo_a, nodo_b, peso)
        self.agregar_arista(nodo_b, nodo_a, peso)
    
    # --- Aquí irá el método de Dijkstra más adelante ---
    # def encontrar_ruta_mas_corta(self, inicio, fin):
    #     pass
    