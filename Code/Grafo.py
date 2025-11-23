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
        peso: Distancia en METROS REALES
        """
        if origen not in self.adyacencia: self.agregar_nodo(origen)
        if destino not in self.adyacencia: self.agregar_nodo(destino)
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

    def dijkstra(self, nodo_inicio, nodo_fin, modo_transporte="caminar"):
        # --- VELOCIDADES EN METROS POR MINUTO ---
        # Caminar promedio: 5 km/h = 83 m/min
        # Auto ciudad: 40 km/h = 666 m/min
        VELOCIDAD_CAMINAR = 83.0  
        VELOCIDAD_AUTO    = 666.0 

        tiempos = {nodo: float('inf') for nodo in self.adyacencia}
        tiempos[nodo_inicio] = 0
        predecesores = {nodo: None for nodo in self.adyacencia}
        cola_prioridad = [(0, nodo_inicio)]

        while cola_prioridad:
            tiempo_actual, nodo_actual = heapq.heappop(cola_prioridad)

            if nodo_actual == nodo_fin:
                break

            if tiempo_actual > tiempos[nodo_actual]:
                continue

            for vecino, distancia_metros, tipo_via in self.adyacencia[nodo_actual]:
                
                # 1. BLOQUEO DE AUTO EN PARQUE
                if modo_transporte == "auto" and tipo_via == "peatonal":
                    continue 
                
                # 2. DEFINIR VELOCIDAD
                velocidad = VELOCIDAD_CAMINAR
                if modo_transporte == "auto":
                    velocidad = VELOCIDAD_AUTO
                
                # 3. TIEMPO = DISTANCIA (m) / VELOCIDAD (m/min)
                tiempo_tramo = distancia_metros / velocidad
                
                nuevo_tiempo = tiempo_actual + tiempo_tramo

                if nuevo_tiempo < tiempos[vecino]:
                    tiempos[vecino] = nuevo_tiempo
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nuevo_tiempo, vecino))

        ruta = []
        actual = nodo_fin
        if tiempos[nodo_fin] == float('inf'):
            return [], float('inf')

        while actual is not None:
            ruta.insert(0, actual)
            actual = predecesores[actual]

        return ruta, tiempos[nodo_fin]