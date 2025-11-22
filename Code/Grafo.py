import heapq  
import math

class Grafo:
    def __init__(self):
        """
        Inicializa el grafo.
        - self.adyacencia: Diccionario que guarda las conexiones. 
          Clave: Nombre del nodo, Valor: Lista de tuplas (vecino, peso)
        - self.coordenadas: Diccionario para guardar (x, y) de cada nodo para dibujarlo.
        """
        self.adyacencia = {}
        self.coordenadas = {}

    def agregar_nodo(self, nombre_nodo: str, x: int = 0, y: int = 0):
        """
        Agrega un nodo (una ubicación) al grafo si no existe.
        Recibe coordenadas x, y para poder dibujarlo en la interfaz más tarde.
        """
        if nombre_nodo not in self.adyacencia:
            self.adyacencia[nombre_nodo] = []
            self.coordenadas[nombre_nodo] = (x, y)
            # print(f"✅ Nodo '{nombre_nodo}' creado en ({x}, {y}).")

    def agregar_arista(self, origen: str, destino: str, peso: float):
        """
        Crea una conexión dirigida de Origen -> Destino.
        """
        # Aseguramos que los nodos existan antes de conectar
        if origen not in self.adyacencia:
            print(f"⚠️ Advertencia: El nodo '{origen}' se creó automáticamente sin coordenadas.")
            self.agregar_nodo(origen)
        if destino not in self.adyacencia:
            print(f"⚠️ Advertencia: El nodo '{destino}' se creó automáticamente sin coordenadas.")
            self.agregar_nodo(destino)

        # Agregamos la conexión a la lista de adyacencia
        self.adyacencia[origen].append((destino, peso))
        # print(f"🔗 Conexión: {origen} -> {destino} ({peso} min/km)")

    def agregar_arista_doble_sentido(self, nodo_a: str, nodo_b: str, peso: float):
        """
        Crea una calle de doble sentido (A -> B y B -> A).
        """
        self.agregar_arista(nodo_a, nodo_b, peso)
        self.agregar_arista(nodo_b, nodo_a, peso)

    def obtener_vecinos(self, nodo: str):
        """
        Devuelve la lista de vecinos de un nodo. Útil para Dijkstra.
        """
        return self.adyacencia.get(nodo, [])

    def obtener_coordenadas(self, nodo: str):
        """
        Devuelve (x, y) de un nodo. Útil para la interfaz gráfica.
        """
        return self.coordenadas.get(nodo, (0, 0))

    def dijkstra(self, nodo_inicio, nodo_fin):
        """
        Implementa el algoritmo de Dijkstra para encontrar la ruta más corta.
        Retorna: (lista_de_nodos_ruta, distancia_total)
        """
        # 1. Estructuras de datos iniciales
        distancias = {nodo: float('inf') for nodo in self.adyacencia}
        distancias[nodo_inicio] = 0
        
        # Guardamos de dónde venimos para reconstruir la ruta al final
        predecesores = {nodo: None for nodo in self.adyacencia}
        
        # Cola de prioridad: almacena tuplas (distancia_acumulada, nodo_actual)
        cola_prioridad = [(0, nodo_inicio)]

        while cola_prioridad:
            distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

            # Si llegamos al destino, podemos detenernos (optimización)
            if nodo_actual == nodo_fin:
                break

            # Si encontramos una distancia mayor a la ya conocida, la ignoramos
            if distancia_actual > distancias[nodo_actual]:
                continue

            # Explorar vecinos
            for vecino, peso in self.adyacencia[nodo_actual]:
                nueva_distancia = distancia_actual + peso

                # Si encontramos un camino más corto hacia el vecino
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino))

        # 2. Reconstrucción del camino (Backtracking)
        ruta = []
        actual = nodo_fin
        
        # Si la distancia es infinita, es que no hay camino
        if distancias[nodo_fin] == float('inf'):
            return [], float('inf')

        while actual is not None:
            ruta.insert(0, actual) # Insertamos al inicio para invertir el orden
            actual = predecesores[actual]

        return ruta, distancias[nodo_fin]
    def obtener_nodo_mas_cercano(self, x_clic, y_clic):
        """
        Busca en todo el grafo cuál es el nodo más cercano a las coordenadas (x, y).
        Retorna: (nombre_nodo, distancia)
        """
        nodo_mas_cercano = None
        distancia_minima = float('inf')

        for nodo, (nx, ny) in self.coordenadas.items():
            # Distancia Euclideana (Pitagoras)
            dist = math.sqrt((nx - x_clic)**2 + (ny - y_clic)**2)
            
            if dist < distancia_minima:
                distancia_minima = dist
                nodo_mas_cercano = nodo

        return nodo_mas_cercano, distancia_minima