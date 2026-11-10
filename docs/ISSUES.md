# Issues del Proyecto - Kiniela Predictor Equipo 2

**Repositorio**: https://github.com/IA-P1-BCN/kiniela-predictor-equipo2  
**Product Owner**: Mariana  
**Scrum Master**: Anna

Clasificación multiclase (6 clases) del tipo de resultado de un partido de fútbol orientado a kinielas.

| Clase | Significado |
| --- | --- |
| 0 | Victoria local clara |
| 1 | Victoria local ajustada |
| 2 | Empate |
| 3 | Victoria visitante ajustada |
| 4 | Victoria visitante clara |
| 5 | Partido de muchos goles (4+ goles) |

## Equipo

| Persona | Rol | Épicas |
| --- | --- | --- |
| Anna | Scrum Master + Data & EDA Lead | Datos, feature engineering y EDA |
| Cala | Modeling Lead | Modelado, optimización y métricas |
| Eva | App & Backend Lead | Streamlit, Docker, base de datos y despliegue |
| Mariana | Product Owner + MLOps & Neural Networks Lead | Red neuronal, data drift, tests y MLOps |

## Cómo usar este backlog

1. Crear en GitHub una issue por cada bloque de este documento.
2. Copiar la descripción y los criterios de aceptación.
3. Asignar a la persona indicada y etiquetar con la épica.
4. Usar la plantilla de `.github/ISSUE_TEMPLATE/tarea.md` para cualquier issue nueva.
5. Dar una issue por cerrada solo cuando todos sus criterios están cumplidos.

## Definición de hecho

- El código o el documento vive en el repositorio y otra persona del equipo puede ejecutarlo o leerlo.
- Se cumplen todos los criterios de aceptación de la issue.
- No hay secretos, tokens ni credenciales en el repositorio.
- Si cambia un flujo de uso, el `README.md` queda actualizado.

## Resumen

| Issue | Título | Asignado a | Depende de |
| --- | --- | --- | --- |
| #1 | Preparación del dataset | Anna | — |
| #2 | Creación de la variable objetivo | Anna | #1 |
| #3 | Feature engineering | Anna | #1, #2 |
| #4 | Análisis exploratorio (EDA) | Anna | #2, #3 |
| #5 | Modelo baseline | Cala | #2, #3 |
| #6 | Modelos ensemble | Cala | #5 |
| #7 | Optimización y control de overfitting | Cala | #6 |
| #8 | Informe de métricas | Cala | #7 |
| #9 | Aplicación Streamlit | Eva | #8 |
| #10 | Dockerización | Eva | #9 |
| #11 | Base de datos y feedback | Eva | #9 |
| #12 | Despliegue | Eva | #10, #11 |
| #13 | Red neuronal | Mariana | #5, #6 |
| #14 | Monitoreo de data drift | Mariana | #3 |
| #15 | Tests unitarios | Mariana | #2, #8 |
| #16 | Documentación MLOps | Mariana | #11, #13, #14, #15 |
| #17 | Documentación y presentaciones | Todo el equipo (Mariana coordina) | #8, #12, #16 |
| #18 | Gestión del proyecto | Anna | — (continua) |

---

## Épica 1: Datos y EDA (Asignada a Anna)

Etiquetas sugeridas: `epic:datos`, `datos`, `eda`

### Issue #1: Preparación del Dataset

**Asignado a**: Anna  
**Etiquetas**: `datos`  
**Descripción**: Descargar, unificar y limpiar el dataset histórico de partidos de fútbol.

**Criterios de aceptación**:

- [ ] La fuente queda documentada (Football-Data.co.uk o equivalente), con temporadas y competiciones incluidas.
- [ ] Los partidos quedan unificados en un único dataset histórico.
- [ ] Los datos están limpios: sin duplicados de partido y sin valores nulos en columnas críticas (fecha, equipos y goles).
- [ ] El archivo resultante está guardado en `data/`, con raw y procesado separados.
- [ ] El proceso es reproducible mediante script o notebook, y el `README.md` indica cómo regenerar el dataset.

### Issue #2: Creación de la variable objetivo

**Asignado a**: Anna  
**Etiquetas**: `datos`  
**Depende de**: #1  
**Descripción**: Crear la columna `target` con las 6 clases según las reglas definidas.

**Criterios de aceptación**:

- [ ] La función de etiquetado está implementada, es reutilizable y está documentada.
- [ ] Las reglas escritas definen el umbral entre victoria clara y victoria ajustada.
- [ ] Las reglas escritas definen la precedencia de la clase 5 (4+ goles) frente al resto de clases.
- [ ] `target` solo contiene los valores 0, 1, 2, 3, 4 y 5, sin nulos.
- [ ] La distribución de clases está calculada, visualizada y comentada (incluido el desbalance).

### Issue #3: Feature Engineering

**Asignado a**: Anna  
**Etiquetas**: `datos`, `features`  
**Depende de**: #1, #2  
**Descripción**: Crear variables de forma reciente, promedios de goles, diferencia de rendimiento y localía.

**Criterios de aceptación**:

- [ ] Existen features de forma reciente, promedio de goles, diferencia de rendimiento y localía.
- [ ] Cada feature tiene una justificación breve (qué aporta a la kiniela y por qué).
- [ ] Las features históricas usan solo información anterior al partido, sin fuga de datos del resultado actual.
- [ ] El código es modular y reutilizable desde `src/`, no solo desde un notebook.
- [ ] El dataset de modelado, con `target` y features, queda guardado en `data/` y documentado.

### Issue #4: Análisis Exploratorio (EDA)

**Asignado a**: Anna  
**Etiquetas**: `eda`  
**Depende de**: #2, #3  
**Descripción**: Realizar un EDA completo con visualizaciones específicas para clasificación multiclase.

**Criterios de aceptación**:

- [ ] El notebook de EDA está terminado en `notebooks/` y se ejecuta de principio a fin.
- [ ] Incluye la distribución de partidos por clase.
- [ ] Incluye la correlación entre features y su relación con `target`.
- [ ] Incluye el análisis de goles (totales, diferencia y relación con la clase 5).
- [ ] Cierra con conclusiones accionables para el modelado: desbalance, features candidatas y riesgos.

---

## Épica 2: Modelado (Asignada a Cala)

Etiquetas sugeridas: `epic:modelado`, `modelado`, `metricas`

### Issue #5: Modelo Baseline

**Asignado a**: Cala  
**Etiquetas**: `modelado`  
**Depende de**: #2, #3  
**Descripción**: Entrenar un modelo baseline (Random Forest o Logistic Regression) con StratifiedKFold.

**Criterios de aceptación**:

- [ ] Hay un baseline de referencia (clasificador de clase mayoritaria o estratificado) con su métrica.
- [ ] El modelo baseline (Random Forest o Logistic Regression) se entrena con `StratifiedKFold`.
- [ ] La semilla y el esquema de validación quedan fijos y documentados para poder comparar después.
- [ ] Se reportan, como mínimo, accuracy y F1 macro de la validación cruzada.
- [ ] El código de entrenamiento vive en `src/` y se puede volver a ejecutar.

### Issue #6: Modelos Ensemble

**Asignado a**: Cala  
**Etiquetas**: `modelado`  
**Depende de**: #5  
**Descripción**: Entrenar y comparar XGBoost y LightGBM.

**Criterios de aceptación**:

- [ ] XGBoost y LightGBM se entrenan con el mismo esquema de validación que el baseline.
- [ ] La comparación incluye baseline, XGBoost y LightGBM con accuracy, F1 macro y F1 por clase.
- [ ] Se elige un modelo candidato y la elección está justificada con esas métricas.
- [ ] El código de los dos ensembles es reproducible y comparable entre sí.

### Issue #7: Optimización y control de Overfitting

**Asignado a**: Cala  
**Etiquetas**: `modelado`  
**Depende de**: #6  
**Descripción**: Optimizar hiperparámetros y garantizar overfitting inferior al 5%.

**Criterios de aceptación**:

- [ ] La búsqueda de hiperparámetros (grid, random u Optuna) queda descrita con el espacio explorado.
- [ ] Los hiperparámetros finales están registrados junto al modelo elegido.
- [ ] El overfitting es inferior al 5%: la diferencia absoluta entre la métrica de train y la de validación es menor que 0.05.
- [ ] La métrica usada para medir ese gap (accuracy o F1 macro) está declarada.
- [ ] Hay una tabla o curva que muestra el gap de generalización antes y después de la optimización.

### Issue #8: Informe de Métricas

**Asignado a**: Cala  
**Etiquetas**: `modelado`, `metricas`  
**Depende de**: #7  
**Descripción**: Generar métricas completas (accuracy, precision/recall/F1 por clase, matriz de confusión, feature importance y análisis de errores).

**Criterios de aceptación**:

- [ ] El informe incluye accuracy global del modelo seleccionado.
- [ ] El informe incluye precision, recall y F1 por cada una de las 6 clases.
- [ ] El informe incluye la matriz de confusión, legible y con las etiquetas de clase.
- [ ] El informe incluye feature importance del modelo seleccionado.
- [ ] El informe incluye análisis de errores: clases más confundidas y ejemplos representativos.
- [ ] El documento está en `docs/` o en un notebook enlazado desde el `README.md`.

---

## Épica 3: Aplicación y Despliegue (Asignada a Eva)

Etiquetas sugeridas: `epic:app`, `app`, `mlops`

### Issue #9: Aplicación Streamlit

**Asignado a**: Eva  
**Etiquetas**: `app`  
**Depende de**: #8  
**Descripción**: Crear la app que permita predecir la clase y muestre las probabilidades.

**Criterios de aceptación**:

- [ ] La app arranca con `streamlit run app/streamlit_app.py`.
- [ ] Permite introducir los datos de un partido, o elegir un ejemplo precargado, y lanzar la predicción.
- [ ] Muestra la clase predicha (0-5) junto con su nombre legible.
- [ ] Muestra las probabilidades de las 6 clases.
- [ ] Una entrada inválida muestra un mensaje claro y no rompe la aplicación.

### Issue #10: Dockerización

**Asignado a**: Eva  
**Etiquetas**: `app`, `devops`  
**Depende de**: #9  
**Descripción**: Crear un Dockerfile funcional del proyecto.

**Criterios de aceptación**:

- [ ] `docker build` termina sin errores.
- [ ] `docker run` levanta la app Streamlit y responde en el puerto expuesto.
- [ ] El `README.md` documenta los comandos de build y run.
- [ ] La imagen no incluye secretos, datasets enormes ni entornos virtuales locales.
- [ ] Existe un `.dockerignore` con exclusiones mínimas (`.git`, `.venv`, cachés y secretos).

### Issue #11: Base de Datos y Feedback

**Asignado a**: Eva  
**Etiquetas**: `app`, `datos`  
**Depende de**: #9  
**Descripción**: Implementar el guardado de predicciones y el feedback del usuario.

**Criterios de aceptación**:

- [ ] Cada predicción se guarda con fecha, entradas, clase predicha y probabilidades.
- [ ] La persona usuaria puede enviar feedback asociado a esa predicción (acierto, error o clase real).
- [ ] El esquema de tablas o colecciones está documentado.
- [ ] Las credenciales se leen de variables de entorno y no están en el repositorio.
- [ ] Se puede consultar un historial mínimo de predicciones y feedback.

### Issue #12: Despliegue

**Asignado a**: Eva  
**Etiquetas**: `devops`  
**Depende de**: #10, #11  
**Descripción**: Dejar la aplicación desplegada (Render, Railway o similar).

**Criterios de aceptación**:

- [ ] La aplicación está desplegada en Render, Railway o un servicio equivalente.
- [ ] La URL pública funciona y permite hacer una predicción de punta a punta.
- [ ] La URL está enlazada en el `README.md`.
- [ ] Las variables de entorno necesarias están listadas, sin valores secretos.
- [ ] El servicio reinicia la app con el comando documentado y queda accesible tras el deploy.

---

## Épica 4: MLOps y Nivel Experto (Asignada a Mariana)

Etiquetas sugeridas: `epic:mlops`, `mlops`, `testing`

### Issue #13: Red Neuronal

**Asignado a**: Mariana  
**Etiquetas**: `modelado`, `mlops`  
**Depende de**: #5, #6  
**Descripción**: Entrenar una red neuronal multiclase y compararla con los modelos ensemble.

**Criterios de aceptación**:

- [ ] La red tiene 6 salidas y entrenamiento multiclase reproducible.
- [ ] Usa la misma preparación de datos y un esquema de validación comparable al de los ensembles.
- [ ] Early stopping, regularización o una estrategia equivalente queda documentada.
- [ ] Hay una tabla que compara la red con el mejor ensemble (accuracy, F1 macro y F1 por clase).
- [ ] El código vive en `src/` y se puede volver a entrenar con una semilla fija.

### Issue #14: Monitoreo de Data Drift

**Asignado a**: Mariana  
**Etiquetas**: `mlops`  
**Depende de**: #3  
**Descripción**: Implementar una detección básica de data drift.

**Criterios de aceptación**:

- [ ] Existe un conjunto de referencia (datos de entrenamiento) y un conjunto nuevo a comparar.
- [ ] El detector compara features clave con un método explícito (PSI, KS o variación de media y desviación).
- [ ] Hay un umbral documentado que marca drift sí o no por feature y a nivel global.
- [ ] Una función o script genera un informe legible con el resultado.
- [ ] El `README.md` o `docs/` explica cómo ejecutarlo.

### Issue #15: Tests Unitarios

**Asignado a**: Mariana  
**Etiquetas**: `testing`  
**Depende de**: #2, #8  
**Descripción**: Crear tests para validación de datos, predicciones y métricas.

**Criterios de aceptación**:

- [ ] Hay tests de validación de datos: esquema, nulos críticos, rangos y `target` dentro de 0-5.
- [ ] Hay tests de predicción: forma de la salida, clase dentro de rango y probabilidades que suman aproximadamente 1.
- [ ] Hay tests de métricas con un caso fijo y resultado esperado conocido.
- [ ] `pytest` pasa en local.
- [ ] El `README.md` indica el comando para ejecutar la suite.

### Issue #16: Documentación MLOps

**Asignado a**: Mariana  
**Etiquetas**: `mlops`, `docs`  
**Depende de**: #11, #13, #14, #15  
**Descripción**: Documentar el flujo de versiones de modelos, feedback y monitoreo.

**Criterios de aceptación**:

- [ ] El documento describe cómo se versiona un modelo: qué se guarda, dónde y cómo se promociona a la app.
- [ ] El documento describe el flujo de feedback, desde la app hasta su uso en una revisión o reentrenamiento.
- [ ] El documento describe el flujo de monitoreo y data drift, incluyendo qué hacer si salta la alerta.
- [ ] El documento está en `docs/` y enlazado desde el `README.md`.
- [ ] Una persona del equipo puede seguir el flujo sin explicación oral.

---

## Issues Transversales

### Issue #17: Documentación y Presentaciones

**Asignado a**: Todo el equipo (coordinado por Mariana)  
**Etiquetas**: `docs`  
**Depende de**: #8, #12, #16  
**Descripción**: Informe técnico final, presentación de negocio y presentación técnica.

**Criterios de aceptación**:

- [ ] El informe técnico final cubre datos, target, features, modelos, métricas, app y MLOps.
- [ ] La presentación de negocio explica el problema de la kiniela, el valor del producto y el resultado.
- [ ] La presentación técnica explica arquitectura, validación, métricas por clase y límites del modelo.
- [ ] Los tres entregables están en el repositorio o enlazados desde `docs/`.
- [ ] Mariana, como Product Owner, revisa que el relato coincide con el producto entregado.

### Issue #18: Gestión del Proyecto

**Asignado a**: Anna (Scrum Master)  
**Etiquetas**: `gestion`  
**Descripción**: Mantener el tablero actualizado y facilitar las dailies.

**Criterios de aceptación**:

- [ ] Las issues de este documento están creadas en GitHub y visibles en el tablero del proyecto.
- [ ] Cada issue tiene responsable, estado y épica.
- [ ] Las dailies usan `docs/DAILY_TEMPLATE.md` y dejan constancia de bloqueos.
- [ ] El tablero se actualiza al menos en cada daily.
- [ ] Los bloqueos tienen dueño y siguiente paso antes de cerrar la daily.
