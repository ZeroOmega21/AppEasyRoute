import math

def obtener_info_coordenada(event, offset_x, offset_y, factor_escala, ancho_max, alto_max):
    """Calcula la coordenada real basada en el clic."""
    clic_x = event.x
    clic_y = event.y

    try:
        real_x = int((clic_x - offset_x) / factor_escala)
        real_y = int((clic_y - offset_y) / factor_escala)
    except ZeroDivisionError:
        return None

    if real_x < 0 or real_x > ancho_max or real_y < 0 or real_y > alto_max:
        print(f"[ERROR] Clic fuera: ({real_x}, {real_y})")
        return None

    texto_copiar = f'"NUEVO_LUGAR" : ({real_x}, {real_y}),'
    print(f"[COORDENADA] Clic Derecho -> Copia:  {texto_copiar}")
    return real_x, real_y

def es_zona_protegida(nombre_grupo):
    return ("Parque" in nombre_grupo or 
            "Picnic" in nombre_grupo or 
            "Lago"   in nombre_grupo or 
            "Acceso" in nombre_grupo)

def conectar_tramos_con_sentido(mapa, nodos_calle, coords_calle, nombre_calle, sentidos_dict, tipo_via, escala_metros):
    sentido = sentidos_dict.get(nombre_calle, "DOBLE")

    for i in range(len(nodos_calle) - 1):
        nodo_A = nodos_calle[i]
        nodo_B = nodos_calle[i+1]
        
        x1, y1 = coords_calle[i]
        x2, y2 = coords_calle[i+1]
        dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dist_metros = dist_px * escala_metros
        
        if tipo_via == "peatonal":
            mapa.agregar_arista_doble_sentido(nodo_A, nodo_B, peso=dist_metros, tipo="peatonal")
        elif sentido == "DOBLE":
            mapa.agregar_arista_doble_sentido(nodo_A, nodo_B, peso=dist_metros, tipo="universal")
        elif sentido == "ARRIBA": 
            mapa.agregar_arista(nodo_A, nodo_B, peso=dist_metros, tipo="universal")
            mapa.agregar_arista(nodo_B, nodo_A, peso=dist_metros, tipo="peatonal")
        elif sentido == "ABAJO":
            mapa.agregar_arista(nodo_B, nodo_A, peso=dist_metros, tipo="universal")
            mapa.agregar_arista(nodo_A, nodo_B, peso=dist_metros, tipo="peatonal")

def conectar_cruces_inteligentes(mapa, todos_los_nodos, escala_metros):
    print("--- Calculando intersecciones y accesos ---")
    
    UMBRAL_CALLES_PX = 40   
    UMBRAL_LUGARES_PX = 80  
    count_conexiones = 0

    for i in range(len(todos_los_nodos)):
        nodo_a = todos_los_nodos[i]
        for j in range(i + 1, len(todos_los_nodos)):
            nodo_b = todos_los_nodos[j]

            grupo_a = nodo_a["grupo"]
            grupo_b = nodo_b["grupo"]
            
            # --- CAMBIO DE NOMBRE AQUÍ ---
            es_punto_interes_a = grupo_a == "PUNTO_INTERES"
            es_punto_interes_b = grupo_b == "PUNTO_INTERES"

            # Regla 0: No conectar mismos grupos salvo Puntos de Interés
            if grupo_a == grupo_b and not es_punto_interes_a:
                continue

            # Cortafuegos
            es_calle_a = "Calle" in grupo_a or "Av_" in grupo_a or "Pasaje" in grupo_a or "Camino" in grupo_a
            es_calle_b = "Calle" in grupo_b or "Av_" in grupo_b or "Pasaje" in grupo_b or "Camino" in grupo_b
            es_parque_interno_a = es_zona_protegida(grupo_a) and not es_punto_interes_a
            es_parque_interno_b = es_zona_protegida(grupo_b) and not es_punto_interes_b

            if (es_calle_a and es_parque_interno_b) or (es_calle_b and es_parque_interno_a):
                continue 

            # Radio dinámico
            radio_limite = UMBRAL_LUGARES_PX if (es_punto_interes_a or es_punto_interes_b) else UMBRAL_CALLES_PX
            
            dist_px = math.sqrt((nodo_a["x"] - nodo_b["x"])**2 + (nodo_a["y"] - nodo_b["y"])**2)

            if dist_px < radio_limite:
                dist_metros = dist_px * escala_metros
                
                # Penalización de acceso
                es_acceso_edificio = (es_punto_interes_a or es_punto_interes_b)
                peso_final = dist_metros + (150 if es_acceso_edificio else 0)

                mapa.agregar_arista_doble_sentido(nodo_a["nombre"], nodo_b["nombre"], peso=peso_final, tipo="universal")
                count_conexiones += 1
    
    print(f"--- Mapa listo: {count_conexiones} intersecciones calculadas ---")

def conectar_tramos_con_sentido(mapa, nodos_calle, coords_calle, nombre_calle, sentidos_dict, tipo_via, escala_metros):
    # 1. Obtener el sentido configurado para esta calle (Por defecto "DOBLE")
    sentido = sentidos_dict.get(nombre_calle, "DOBLE")

    # 2. Recorrer los tramos
    for i in range(len(nodos_calle) - 1):
        nodo_A = nodos_calle[i]     # Nodo actual
        nodo_B = nodos_calle[i+1]   # Siguiente nodo
        
        # Calcular distancia real (Pitágoras)
        x1, y1 = coords_calle[i]
        x2, y2 = coords_calle[i+1]
        dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dist_metros = dist_px * escala_metros
        
        # 3. Aplicar lógica de conexión según el sentido
        
        # CASO A: PARQUES O CALLES PEATONALES (Siempre doble vía para peatones, prohibido autos)
        if tipo_via == "peatonal":
            mapa.agregar_arista_doble_sentido(nodo_A, nodo_B, peso=dist_metros, tipo="peatonal")
        
        # CASO B: CALLE DOBLE MANO (Autos y peatones van y vienen)
        elif sentido == "DOBLE":
            mapa.agregar_arista_doble_sentido(nodo_A, nodo_B, peso=dist_metros, tipo="universal")
        
        # CASO C: SENTIDO "ARRIBA" (A -> B)
        elif sentido == "ARRIBA": 
            # Auto: Solo Ida
            mapa.agregar_arista(nodo_A, nodo_B, peso=dist_metros, tipo="universal")
            # Peatón: Puede volver por la vereda
            mapa.agregar_arista(nodo_B, nodo_A, peso=dist_metros, tipo="peatonal")
            
        # CASO D: SENTIDO "ABAJO" (B -> A)
        elif sentido == "ABAJO":
            # Auto: Solo Vuelta
            mapa.agregar_arista(nodo_B, nodo_A, peso=dist_metros, tipo="universal")
            # Peatón: Puede subir por la vereda
            mapa.agregar_arista(nodo_A, nodo_B, peso=dist_metros, tipo="peatonal")


def obtener_info_coordenada(event, offset_x, offset_y, factor_escala, ancho_max, alto_max):
    
    clic_x = event.x
    clic_y = event.y

    # 1. Matemática Inversa: (Pantalla -> Real)
    try:
        real_x = int((clic_x - offset_x) / factor_escala)
        real_y = int((clic_y - offset_y) / factor_escala)
    except ZeroDivisionError:
        return None

    # 2. Validación: ¿Cayó dentro de la imagen?
    if real_x < 0 or real_x > ancho_max or real_y < 0 or real_y > alto_max:
        print(f"[ERROR] Clic fuera de los límites del mapa: ({real_x}, {real_y})")
        return None

    # 3. Imprimir en consola con formato útil
    texto_copiar = f'"NUEVO_LUGAR" : ({real_x}, {real_y}),'
    
    # --- CORRECCIÓN: Quitamos el emoji para evitar el crash en Windows ---
    print(f"[COORDENADA] Clic Derecho detectado -> Copia esto:  {texto_copiar}")

    # Devolvemos las coordenadas para que la interfaz pueda dibujar un punto
    return real_x, real_y