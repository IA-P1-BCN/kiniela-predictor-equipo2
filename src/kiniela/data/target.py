"""Etiquetado de las 6 clases de la kiniela.

Clases Kiniela (prioridad de decisión):
1. Clase 5: 4+ goles TOTAL → precedencia absoluta sobre todo
2. Umbral victoria clara vs ajustada: diferencia de goles >= 3 = clara, < 3 = ajustada
3. Clases 0-4 según resultado y margen

Reglas detalladas:
- Clara: diferencia de goles >= 3 (ej: 3-0, 4-0)
- Ajustada: diferencia de goles 1 o 2 (ej: 2-0, 2-1, 1-0)
- Empate: goles iguales

Precedencia absoluta Clase 5 (4+ goles):
- 2-2 con 4 goles → clase 5 (no empate clase 2)
- 3-1 con 4 goles → clase 5 (no victoria local clara clase 0)
- 1-3 con 4 goles → clase 5 (no victoria visitante ajustada clase 3)
- 0-4 con 4 goles → clase 5 (no victoria visitante clara clase 4)

Ejemplos:
    build_target(2, 0) → 1 (victoria local ajustada)
    build_target(3, 0) → 0 (victoria local clara)
    build_target(2, 2) → 5 (precedencia clase 5 por 4 goles)
    build_target(1, 3) → 5 (precedencia clase 5 por 4 goles)
    build_target(0, 2) → 3 (victoria visitante ajustada)
"""


def build_target(home_goals: int, away_goals: int) -> int:
    """
    Devuelve la clase 0-5 de un partido a partir de los goles.
    
    Args:
        home_goals: Goles del equipo local (HomeTeam)
        away_goals: Goles del equipo visitante (AwayTeam)
        
    Returns:
        int: Clase de Kiniela (0-5)
        
    Raises:
        ValueError: Si alguno de los goles es negativo
        
    Ejemplos:
        >>> build_target(2, 0)
        1
        >>> build_target(3, 0)
        0
        >>> build_target(2, 2)
        5  # precedencia clase 5 por 4 goles totales
        >>> build_target(1, 3)
        5  # precedencia clase 5 por 4 goles totales
    """
    
    # Validación inicial
    if home_goals < 0 or away_goals < 0:
        raise ValueError("Los goles no pueden ser negativos.")
    
    fh = int(home_goals)
    ah = int(away_goals)
    
    total_goles = fh + ah
    
    # --- PASO 1: Precedencia absoluta Clase 5 (4+ goles totales) ---
    if total_goles >= 4:
        return 5
    
    # Si llegamos aquí, total_goles < 4, así que no hay precedencia clase 5
    
    diferencia = fh - ah
    
    # --- PASO 2: Clasificar según resultado y margen ---
    
    # Victoria Local (fh > ah)
    if fh > ah:
        # Victoria local clara si diferencia >= 3
        if diferencia >= 3:
            return 0  # Victoria local clara
        
        # Sino, es victoria local ajustada (diferencia 1 o 2)
        return 1  # Victoria local ajustada
    
    # --- Empate (fh == ah) ---
    elif fh == ah:
        # Si no hay precedencia clase 5 (ya comprobado arriba), 
        # cualquier empate es clase 2
        return 2  # Empate
    
    # --- Victoria Visitante (ah > fh) ---
    else:  # ah > fh
        # Victoria visitante clara si diferencia >= 3
        if diferencia <= -3:  # diferencia negativa con magnitud >= 3
            return 4  # Victoria visitante clara
        
        # Sino, es victoria visitante ajustada (diferencia -1 o -2)
        return 3  # Victoria visitante ajustada
