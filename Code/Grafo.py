import heapq
import math

class Grafo:
    def __init__(self):
        self.adyacencia = {}
        self.coordenadas = {}

    def agregar_nodo(self, nombre_nodo: str, x: int = 0, y: int = 0):
        if nombre_nodo not in self.adyacencia:
            self.adyacencia[nombre_nodo] = []
            self.coordenadas[nombre_nodo] = (x, y)

    def agregar_arista(self, origen, destino, peso, tipo="universal"):
        """
        tipo: 'universal' (autos y peatones) o 'peatonal' (solo peatones)
        """
        # Aseguramos que existan los nodos
        if origen not in self.adyacencia: self.agregar_nodo(origen)
        if destino not in self.adyacencia: self.agregar_nodo(destino)

        # Guardamos la conexión con su TIPO
        self.adyacencia[origen].append((destino, peso, tipo))

    def agregar_arista_doble_sentido(self, nodo_a, nodo_b, peso, tipo="universal"):
        self.agregar_arista(nodo_a, nodo_b, peso, tipo)
        self.agregar_arista(nodo_b, nodo_a, peso, tipo)

    def obtener_vecinos(self, nodo):
        return self.adyacencia.get(nodo, [])

    def obtener_coordenadas(self, nodo):
        return self.coordenadas.get(nodo, (0, 0))
    
    def obtener_nodo_mas_cercano(self, x_clic, y_clic):
        nodo_mas_cercano = None
        distancia_minima = float('inf')
        for nodo, (nx, ny) in self.coordenadas.items():
            dist = math.sqrt((nx - x_clic)**2 + (ny - y_clic)**2)
            if dist < distancia_minima:
                distancia_minima = dist
                nodo_mas_cercano = nodo
        return nodo_mas_cercano, distancia_minima

    # --- DIJKSTRA MEJORADO ---
    def dijkstra(self, nodo_inicio, nodo_fin, modo_transporte="caminar"):
        """
        modo_transporte: 'auto' o 'caminar'
        """
        distancias = {nodo: float('inf') for nodo in self.adyacencia}
        distancias[nodo_inicio] = 0
        predecesores = {nodo: None for nodo in self.adyacencia}
        cola_prioridad = [(0, nodo_inicio)]

        while cola_prioridad:
            distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

            if nodo_actual == nodo_fin:
                break

            if distancia_actual > distancias[nodo_actual]:
                continue

            # Iteramos sobre los vecinos
            for vecino, peso, tipo_via in self.adyacencia[nodo_actual]:
                
                # --- REGLA DE BLOQUEO ---
                # Si voy en AUTO y la calle es PEATONAL, no puedo pasar.
                if modo_transporte == "auto" and tipo_via == "peatonal":
                    continue 
                
                # (Opcional) Si vas en auto por calle normal, cuesta menos tiempo (es más rápido)
                costo_tramo = peso
                if modo_transporte == "auto" and tipo_via == "universal":
                    costo_tramo = peso / 3  # El auto es 3 veces más rápido
                
                nueva_distancia = distancia_actual + costo_tramo

                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino))

        # Reconstruir ruta
        ruta = []
        actual = nodo_fin
        if distancias[nodo_fin] == float('inf'):
            return [], float('inf') # No hay camino

        while actual is not None:
            ruta.insert(0, actual)
            actual = predecesores[actual]

        return ruta, distancias[nodo_fin]