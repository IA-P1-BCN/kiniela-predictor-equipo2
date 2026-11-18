# 9. Conclusiones, límites y próximos pasos

**Quién:** Mariana compila · **Aportan:** Anna, Carla, Eva, Mariana · **Estado a 18/11/2026** (entrega: 18/11, 23:59)

Compilada a partir de las secciones 1 a 8 y de las aportaciones de la issue #17. Cada bloque recoge un límite real y un aprendizaje de su parte.

## 9.1 Qué hemos conseguido

- Un problema de **6 clases** con sentido de negocio: el tipo de partido, no solo el 1X2 (sección 1).
- **Datos reales** de 9 temporadas de la Premier League (3.420 partidos) y **8 features sin fuga de datos**, calculadas igual para entrenar y para predecir (secciones 2 y 3).
- **Modelos comparables:** referencia, Random Forest, XGBoost, LightGBM y una red neuronal, con el mismo `StratifiedKFold` y la misma semilla (secciones 4 y 5).
- Un **modelo final** que dobla a la referencia en F1 macro (0,172 frente a 0,080) con un sobreajuste por debajo del 5 % (gap 0,0496), en producción desde el 16/11 (secciones 4 y 6).
- Una **app pública** que guarda cada predicción con su versión de modelo y el feedback de quien la usa, desplegada con Docker en Render y PostgreSQL en Neon (sección 6).
- Un **circuito de mejora**: export de datos etiquetados, vigilancia del drift con PSI y A/B testing con una regla de promoción fija (secciones 7a y 7b).

## 9.2 Límites

| Parte | Límite | Efecto |
| --- | --- | --- |
| Datos | Solo 8 features de forma y goles recientes; sin cuotas, lesiones, alineaciones ni descanso | El modelo distingue bien local frente a visitante, pero apenas separa el resto de clases |
| Datos | Clases desbalanceadas (la 5 es el 32 %) y frontera estrecha: un gol cambia la clase | La accuracy engaña; hay que decidir con F1 macro |
| Modelos | F1 macro bajo en términos absolutos (0,172); la clase 1 es la peor recuperada (recall 0,098) y la 4 la menos fiable al predecirla | Útil como orientación, no para apostar |
| Modelos | La comparación entre modelos y la red neuronal son de una temporada; el modelo final, de nueve | Las cifras de 4.2 y de la sección 5 no se comparan con las del modelo final |
| Producto | El modelo está fijo desde el 16/11 y el feedback depende de la gente: hoy hay muy pocas respuestas y nadie verifica la clase real | El acierto en tiempo real todavía no dice nada |
| Producto | Plan gratuito de Render (la app se duerme tras 15 minutos) y despliegue manual | La primera visita tarda alrededor de un minuto |
| Operación | El drift y el reentrenamiento se lanzan a mano; no hay un proceso programado | Depende de que alguien lo ejecute con cada jornada nueva |

## 9.3 Aprendizajes

- **Medir antes de decidir.** Con una temporada, el modelo optimizado no superaba a la referencia (0,095 frente a 0,102). Con nueve, el F1 macro se dobló. Más datos ayudaron más que más ajuste.
- **Preferir un modelo defendible.** El ajuste de hiperparámetros bajó un poco el F1 (0,180 → 0,172), pero el gap pasó de 0,505 a 0,0496: el modelo dejó de memorizar.
- **La accuracy engaña con clases desbalanceadas.** La referencia acierta un 44 % en 2023-24 diciendo siempre «clase 5». La red neuronal acertaba más que los árboles por el mismo motivo, y no era mejor modelo.
- **Comprobar con datos reales, no solo con tests.** Al comparar con partidos reales vimos que la app calculaba las features distinto que el entrenamiento y que las fechas en texto colaban partidos futuros. Desde entonces hay una sola función y tests que lo garantizan.
- **Un contrato desacopla la app del modelo.** La app se desplegó desde el primer día con un modelo provisional, y el modelo final entró sin tocar la app.
- **Los tests deben ejecutarse con las dependencias de producción.** Quitar LightGBM del runtime (PR #77) habría roto la carga del modelo con el CI en verde; se detectó en la revisión.
- **La IA ayuda, pero se verifica.** Una IA llegó a afirmar que la fuente de datos estaba caída y generó datos falsos, y la revisión automática de un PR señaló un problema que no existía. Las bitácoras de IA, los tests y la revisión humana lo frenaron (sección 8).

## 9.4 Próximos pasos

**Producto**
- Rellenar la clase real con los resultados oficiales de la misma fuente, en lugar de depender del feedback.
- Plan de pago y despliegue automático para que la app no se duerma.

**Modelo**
- Nuevas features: clasificación, cuotas previas al partido y días de descanso.
- Repetir la comparación de modelos y la red neuronal con las 9 temporadas.

**Operación**
- Programar el drift y el reentrenamiento con cada jornada, y promocionar candidatos con el A/B testing que ya existe.
- Un test de CI que cargue el modelo solo con `requirements.txt`, y migraciones de esquema (Alembic) para la base de datos.
