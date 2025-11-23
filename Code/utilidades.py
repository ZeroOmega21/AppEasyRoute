def obtener_info_coordenada(event, offset_x, offset_y, factor_escala, ancho_max, alto_max):
    """
    Calcula la coordenada real basada en el clic y la escala actual.
    Imprime el formato listo para copiar en datos_mapa.py
    """
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