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

    # --- MÉTODO DE BLOQUEO SELECTIVO ---
    def alternar_bloqueo_zona(self, centro_x, centro_y, radio_metros=30, cerrada=True, afectados="ambos"):
        """
        afectados: 'ambos', 'auto', 'peaton'
        """
        METROS_POR_PIXEL = 0.5 
        PESO_BLOQUEO = 9999999.0 
        radio_px = radio_metros / METROS_POR_PIXEL
        
        nodos_afectados = []
        for nodo, (nx, ny) in self.coordenadas.items():
            dist = math.sqrt((nx - centro_x)**2 + (ny - centro_y)**2)
            if dist <= radio_px:
                nodos_afectados.append(nodo)

        for nodo_origen in nodos_afectados:
            if nodo_origen in self.adyacencia:
                nuevas_conexiones = []
                for (destino, peso_actual, tipo_actual) in self.adyacencia[nodo_origen]:
                    
                    nuevo_peso = peso_actual
                    nuevo_tipo = tipo_actual

                    if cerrada:
                        # --- APLICAR BLOQUEO SEGÚN EL AFECTADO ---
                        if afectados == "ambos":
                            nuevo_peso = PESO_BLOQUEO # Muro físico
                        elif afectados == "auto":
                            nuevo_tipo = "peatonal"   # Convertimos la calle en peatonal
                        elif afectados == "peaton":
                            nuevo_tipo = "solo_auto"  # Prohibido peatones
                    else:
                        # --- DESBLOQUEAR (RESTAURAR) ---
                        # 1. Restaurar Peso
                        if destino in self.coordenadas:
                            x1, y1 = self.coordenadas[nodo_origen]
                            x2, y2 = self.coordenadas[destino]
                            dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                            nuevo_peso = dist_px * METROS_POR_PIXEL
                            if "PUNTO_INTERES" in destino or "LUGAR_VIP" in destino:
                                nuevo_peso += 150
                        else:
                            nuevo_peso = peso_actual

                        # 2. Restaurar Tipo (Lógica inversa inteligente)
                        # Si el nodo tiene nombre de parque, originalmente era peatonal.
                        # Si no, era universal.
                        es_zona_verde = ("Parque" in nodo_origen or "Lago" in nodo_origen or 
                                         "Parque" in destino or "Lago" in destino)
                        
                        nuevo_tipo = "peatonal" if es_zona_verde else "universal"

                    nuevas_conexiones.append((destino, nuevo_peso, nuevo_tipo))
                
                self.adyacencia[nodo_origen] = nuevas_conexiones

    def dijkstra(self, nodo_inicio, nodo_fin, modo_transporte="caminar"):
        VELOCIDAD_CAMINAR = 83.0  
        VELOCIDAD_AUTO    = 666.0 
        UMBRAL_BLOQUEO = 500000 

        tiempos = {nodo: float('inf') for nodo in self.adyacencia}
        tiempos[nodo_inicio] = 0
        predecesores = {nodo: None for nodo in self.adyacencia}
        cola_prioridad = [(0, nodo_inicio)]

        while cola_prioridad:
            tiempo_actual, nodo_actual = heapq.heappop(cola_prioridad)

            if nodo_actual == nodo_fin: break
            if tiempo_actual > tiempos[nodo_actual]: continue

            for vecino, distancia_metros, tipo_via in self.adyacencia[nodo_actual]:
                
                # 1. BLOQUEO FÍSICO (AMBOS)
                if distancia_metros > UMBRAL_BLOQUEO: continue

                # 2. BLOQUEO DE AUTO (Vía peatonal)
                if modo_transporte == "auto" and tipo_via == "peatonal": continue 
                
                # 3. BLOQUEO DE PEATÓN (Vía solo autos - NUEVO)
                if modo_transporte == "caminar" and tipo_via == "solo_auto": continue

                # 4. CÁLCULO
                velocidad = VELOCIDAD_AUTO if modo_transporte == "auto" else VELOCIDAD_CAMINAR
                tiempo_tramo = distancia_metros / velocidad
                
                nuevo_tiempo = tiempo_actual + tiempo_tramo

                if nuevo_tiempo < tiempos[vecino]:
                    tiempos[vecino] = nuevo_tiempo
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nuevo_tiempo, vecino))

        ruta = []
        actual = nodo_fin
        if tiempos[nodo_fin] == float('inf'): return [], float('inf')

        while actual is not None:
            ruta.insert(0, actual)
            actual = predecesores[actual]

        return ruta, tiempos[nodo_fin]