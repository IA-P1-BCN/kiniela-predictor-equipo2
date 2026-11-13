# 1. Problema, objetivo y valor para negocio

**Quién:** Mariana (Product Owner) · **Issue:** #17 · **Estado:** escrita (13/11/2026)

## 1.1 El problema

Una kiniela no pide el marcador exacto: pide el **tipo de resultado**. El 1X2 clásico (local, empate, visitante) es demasiado grueso para decidir. No es lo mismo un 1-0 que un 4-0, ni un 2-2 que un 0-0: el primero es un partido de muchos goles, el segundo un empate trabado.

Kiniela Predictor clasifica cada partido en **una de seis clases**, no en tres. El modelo no sustituye a quien rellena la quiniela: le da una lectura del partido (clase más probable y el resto de probabilidades) para decidir con más información que el instinto.

## 1.2 Las seis clases

Definidas una sola vez en `src/kiniela/config.py`. Anna fija la regla de etiquetado en `src/kiniela/data/target.py` (umbral de diferencia ≥ 2; la clase 5, 4 o más goles, tiene precedencia absoluta).

| Clase | Significado | Para la kiniela |
| --- | --- | --- |
| 0 | Victoria local clara | Local gana por 2 o más, sin ser un festival de goles |
| 1 | Victoria local ajustada | Local gana por 1 |
| 2 | Empate | Igualdad a goles, con menos de 4 en total |
| 3 | Victoria visitante ajustada | Visitante gana por 1 |
| 4 | Victoria visitante clara | Visitante gana por 2 o más, sin 4+ goles |
| 5 | Partido de muchos goles | 4 o más goles, da igual quién gane |

La clase 5 existe porque en una kiniela un 3-1 y un 0-0 no se juegan igual, aunque el primero también sea «victoria local».

## 1.3 Para quién es

No es una herramienta de club ni de scouting. La persona usuaria es quien **rellena una quiniela**: elige un partido, ve la clase y las seis probabilidades, y puede decir después si acertó. Ese feedback alimenta el reentrenamiento ([docs/retraining.md](../retraining.md)).

La app pública: https://kiniela-predictor.onrender.com

## 1.4 Objetivo de este proyecto

Entregar un ciclo completo, no un notebook:

1. Datos reales y `target` de 6 clases (Anna).
2. Features sin fuga del partido que se predice (Anna).
3. Modelos comparables con el mismo `StratifiedKFold` (Cala) y una red neuronal en las mismas condiciones (Mariana).
4. Una app desplegada, con historial y feedback (Eva).
5. Operación: versiones, drift y camino a reentrenar (Mariana y Eva).

## 1.5 Qué no prometemos

- No acertamos el marcador. Acertamos un **tipo** de resultado, y a veces mal: las clases están desbalanceadas (la 5 es frecuente).
- Hasta promocionar un `models/kiniela_model.joblib` que cumpla el [contrato](../model-contract.md), la app usa un modelo de prueba (frecuencias de clase) y lo avisa.
- El plan gratuito de Render duerme la app a los 15 minutos; el primer clic puede tardar.

El valor de negocio, hoy, es poder **usar** la predicción en la web, guardar si falló y tener un procedimiento para mejorar el modelo, no un porcentaje mágico de acierto.
