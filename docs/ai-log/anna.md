# Bitácora de IA · Anna

| Herramienta | Modelo | Coste | Alcance |
| --- | --- | --- | --- |
| Bionic (app) | Qwen 3.5 | Gratuito | Tareas del 11 al 13/11/2026: primeras versiones de #1, #2, #3 y #4 y primeras correcciones de #34 |
| Claude Code (extensión de VS Code) | Claude Opus 5.5 | De pago (plan Pro de Claude) | Entradas desde el 16/11/2026: revisión y corrección de mis tareas (#1, #2, #3, #4 y #34), secciones 2 y 3 del informe y mi guion de la presentación técnica (#17). El agente redacta el código y estas entradas; yo decido, reviso y apruebo cada subida |

## Entradas

### #1 a #4 y #34 Primeras versiones de datos, target y features (11-13/11)

- **Fecha:** 2026-11-11 a 2026-11-13
- **Herramienta y modelo:** Bionic (app), Qwen 3.5.
- **PRs:** #26 (#1 y #2: descarga de datos reales y variable objetivo), #29 (#3: features y descarga de varias temporadas) y #51 y #52 (correcciones de features, #34).
- **Qué se hizo:** descarga y limpieza de la Premier League 2023-24 (`download_premier_league_data`), `build_target` con umbral de 2 goles y la clase 5 por delante (18 tests), primera versión de las features (11 columnas, con `recent_*_form` y `match_momentum`) y primera versión de `build_match_features`.
- **Errores que quedaron y se corrigieron después** (entradas siguientes):
  - Las features de la app no coincidían con las de entrenamiento, las fechas se ordenaban como texto y había features duplicadas (#34).
  - El notebook de EDA de la rama `bionic/tarea-4-eda` nunca llegó a `dev` (#4).
  - La descarga no añadía la columna `Season` con varias temporadas y el CSV procesado se subió al repositorio (#1).
- **Revisión humana:** PRs fusionadas en `dev`.

---

### #34 Features de un partido nuevo: errores corregidos

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** revisar las ramas propias, encontrar los errores y corregirlos.
- **Qué generó el agente:** reescritura de `engineering.py` con un único cálculo por partido (`_match_features`) que comparten `build_features` y `build_match_features`; constante `FEATURE_COLUMNS`; 21 tests nuevos en `tests/test_features.py`; actualización de `docs/tarea-preparacion-dataset.md`.
- **Errores encontrados en el código fusionado (PRs #43, #51, #52 y #54):**
  - `build_match_features` devolvía `form_*_last_5` y `match_diff` siempre vacíos: leía las columnas `ResultHome`/`ResultAway`, que no existen en el histórico.
  - Descartaba el último partido de cada equipo (`Date < max`), así que la app y el entrenamiento no coincidían.
  - El signo de la forma del visitante estaba invertido: una victoria fuera contaba como derrota.
  - Si un equipo no tenía historial, faltaban columnas en lugar de venir vacías.
  - Las fechas `dd/mm/aaaa` se ordenaban como texto (el 01/09 antes que el 11/08), lo que rompía el «solo partidos anteriores».
  - Seguían `recent_*_form` y `match_momentum` (la issue pedía quitarlos) y el docstring no coincidía con el código.
  - La tabla de clases de `docs/tarea-preparacion-dataset.md` sumaba más del 100 %; ahora tiene la distribución real (clase 5: 43,7 %).
- **Aceptado:** función común para entrenamiento y app; `build_match_features` devuelve un DataFrame de una fila con las columnas del modelo, listo para `predict_proba` (contrato de `docs/model-contract.md`).
- **Errores del agente y cómo se corrigieron:** la primera versión leía las fechas ISO con `dayfirst=True` y convertía `2024-09-01` en el 9 de enero; lo detectaron los tests nuevos y ahora se prueba primero el formato ISO.
- **Comprobación:** con el CSV real, las features de la app coinciden con las de entrenamiento en los 380 partidos; `pytest`: 195 tests pasan. Los tests nuevos fallan si se reintroduce la fuga (`<=`) o el signo invertido.
- **Revisión humana:** _pendiente_

---

### #4 EDA: notebook recuperado y corregido

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** llevar a `dev` el EDA de la rama `bionic/tarea-4-eda`, que nunca se fusionó, corrigiendo sus errores. Mariana dio el visto bueno para sustituir su plantilla de `notebooks/01_eda.ipynb`.
- **Errores encontrados en la versión de la rama:**
  - El JSON del notebook estaba roto (Jupyter no lo abría).
  - Nunca se había ejecutado: `build_target` recibía columnas enteras y fallaba en la segunda celda.
  - Las conclusiones no salían de datos (sin salidas) y una recomendaba usar `FTHG`, `FTAG` y la diferencia de goles como features, que es fuga de datos.
  - Usaba features que ya no existen y una correlación de Spearman con `target`, que es nominal.
- **Qué generó el agente:** notebook nuevo que solo llama a `src/kiniela/` (dataset, `target`, distribución de clases, goles, features por clase y correlación entre features) y conclusiones escritas a partir de su ejecución.
- **Comprobación:** todas las celdas se ejecutan con el CSV real; las cifras de las conclusiones son las que imprime el notebook. Se guarda sin salidas, como los demás notebooks del equipo.
- **Revisión humana:** _pendiente_

---

### #17 Informe: sección 3 y guion de la presentación técnica

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** recuperar la sección 3 y el guion de la presentación del commit `cf5334b`, que se subió después de fusionar la PR #51 y nunca llegó a `dev`, y corregir sus errores. Mariana dio el visto bueno para sustituir sus esquemas.
- **Errores encontrados en la versión recuperada:**
  - Sección 3: describía `recent_*_form` y `match_momentum` (ya eliminadas), definía `away_diff_last_5` al revés y tenía una salida de ejemplo y un recuento de tests que no eran reales.
  - Presentación: regla de clases equivocada (diferencia de 3 goles y clase 5 como «4 goles de un equipo»), distribución de clases y tendencia de goles inventadas (una clase con «~X %»), enlaces a archivos que no existen y 12 diapositivas en lugar de 5-6.
- **Qué generó el agente:** sección 3 reescrita con el código de la PR #58 y guion de 6 diapositivas con el formato acordado (se ve, se dice, captura).
- **Comprobación:** todas las cifras salen del CSV real, de los tests o del notebook de EDA.
- **Pendiente:** la sección 2 (`02-datos-y-eda.md`) sigue sin redactar.
- **Revisión humana:** _pendiente_

---

### #17 Informe: sección 2 (datos, variable objetivo y EDA)

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** redactar la sección 2 del informe. Mariana dio el visto bueno para sustituir su esquema de `02-datos-y-eda.md`.
- **Qué generó el agente:** fuente y limpieza de los datos, regla de `target` con su diagrama, distribución de clases y conclusiones del EDA que importan al modelado, enlazando el código en lugar de copiarlo.
- **Comprobación:** todas las cifras se han recalculado con los CSV en bruto y procesado y con `build_target`; los casos de tests citados existen en `tests/test_target.py`.
- **Tras la revisión:** se añadieron las 9 temporadas del modelo final (#66): tabla de 2.1, distribución de clases junto a la de 2023-24 y el resultado de añadir temporadas en 2.4. La distribución, los goles y los equipos se recalcularon descargando las 9 temporadas con `download_premier_league_data` y coinciden con los de la revisión. Los F1 macro salen de la PR #66 y de `models/model_card.json`.
- **Revisión humana:** _pendiente_

---

### #1 Datos: descarga con varias temporadas y documentación corregida

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** revisar si mis tareas tenían errores después de los últimos cambios de `dev` y corregirlos todos.
- **Errores encontrados:**
  - `download_premier_league_data` no añadía la columna `Season` con varias temporadas, aunque su docstring lo decía; las features no reiniciaban el historial en cada temporada. El modelo final lo evitaba descargando temporada a temporada.
  - Si una fecha no se podía leer, se avisaba y la columna se quedaba como texto, que se ordena mal. Además, pandas avisaba porque 2016-17 usa `dd/mm/aa`.
  - Textos de `print` en español y con emojis (fallaban en consolas de Windows sin UTF-8) y un `import` sin usar.
  - El docstring de `target.py` asignaba mal las clases ajustadas («clase 1, 2 o 3», «clase 3 o 4»).
  - `docs/tarea-preparacion-dataset.md`: decía que la descarga guardaba un CSV (no guarda nada, así que el flujo de trabajo no funcionaba), citaba una URL inexistente (`/Premier/{year}.txt`), recomendaba validación temporal (el proyecto usa `StratifiedKFold`) y no explicaba cómo generar el dataset con features y target.
  - `data/processed/premier_league_2023_24.csv` estaba versionado desde mi commit del 11/11, contra la regla de no subir datasets.
- **Qué generó el agente:** la función de descarga reescrita (mismos partidos, `Season` con varias temporadas, error si una fecha no se lee, orden estable, textos en inglés), 7 tests sin red en `tests/test_dataset.py`, el docstring de `target.py` y el documento corregidos, y el CSV sacado del repositorio con `git rm --cached` (sigue en local).
- **Comprobación:** con las 9 temporadas reales la función nueva devuelve los mismos 3.420 partidos que la anterior, 380 por temporada, y 185 sin historial, como la ficha del modelo. Con 2023-24 coincide con el CSV que se saca del repositorio. Los tests nuevos fallan con el código anterior. `pytest` pasa entero.
- **Revisión humana:** _pendiente_

---

### #17 Informe y presentación: puesta al día con el modelo final

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** comprobar si los cambios de `dev` rompían mi trabajo, poner al día la sección 3 y mejorar mi guion de la presentación con las 9 temporadas del modelo final (#66). Completar el campo «Herramienta y modelo» de mis entradas.
- **Qué generó el agente:** sección 3 con los partidos sin historial de las 9 temporadas (3.2) y los límites actualizados (3.6). En el guion: las cifras del modelo final en la diapositiva 2, las dos distribuciones de clases en la 4, la diapositiva 6 cerrando con el salto de 26 a 245 partidos útiles de la clase 4, y una tabla de preguntas probables. Mariana solo había cambiado «Cala» por «Carla» en dos líneas del guion, y se mantiene.
- **Comprobación:** `pytest` y la app sobre `dev` funcionan; las features de la app coinciden con las de entrenamiento en el modelo final. Las cifras de las 9 temporadas (3.420 partidos, 185 sin historial, 3.235 útiles, 245 de la clase 4, `match_diff` 0,45 en la clase 0 y −0,04 en la 4) se recalcularon con `build_features` y `build_target` y coinciden con `models/model_card.json`. El F1 macro del modelo final no se repite en el guion: lo cuentan Carla y Eva en sus partes.
- **Revisión humana:** _pendiente_

---

### #4 EDA y documentación: correcciones tras sacar el CSV del repositorio

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** comprobar que todo funciona después de fusionar las PRs #68 y #69 y solucionar todos los errores antes de subir nada.
- **Errores encontrados:**
  - Al sacar el CSV procesado del repositorio (#68), cada persona lo regenera con `download_premier_league_data`, que guarda las fechas en ISO (`2023-08-11`). El notebook de EDA las leía con `dayfirst=True`, que solo sirve para `dd/mm/aaaa`, y fallaba en la segunda celda de código.
  - El notebook decía que el CSV «se genera con» la descarga, sin el paso de guardarlo, y su conclusión 6 aún proponía añadir temporadas, que ya se hizo en el modelo final.
  - `docs/tarea-preparacion-dataset.md` proponía guardar el dataset de 9 temporadas en `data/processed/`. La app toma los equipos del CSV más reciente de esa carpeta: habría ofrecido 33 equipos, y el modelo rechaza los descendidos.
  - La sección 3 decía que, si se vuelve a meter la fuga, fallan 8 tests; con los tests de la #68 son 9.
  - La parte antigua de esta bitácora no seguía la plantilla del equipo y tenía datos falsos o desfasados: una PR de EDA «fusionada» que nunca llegó a `dev`, features que ya no existen, recuentos de tests viejos y estados de PR caducados.
- **Qué generó el agente:**
  - El notebook usa `_sorted_by_date`, la misma función que convierte las fechas en las features y en `models/final.py`, y acepta los dos formatos. También corrige sus dos textos.
  - Aviso en el documento de preparación del dataset y cifra corregida en la sección 3.
  - Cabecera de la bitácora según la plantilla y la parte antigua resumida en una entrada con datos comprobados con `git` y GitHub.
- **Comprobación:**
  - El notebook se ejecuta entero con el CSV regenerado y con fechas `dd/mm/aaaa`, con la misma salida en los dos casos. Las cifras son las del informe (43,7 %, 80 y 80 partidos, 359 útiles, `match_diff` 0,44 y −0,02).
  - Con un CSV de 9 temporadas, el catálogo de la app ofrece 33 equipos y el modelo rechaza `watford`.
  - Con `<=` en lugar de `<` fallan 9 tests.
  - `pytest` pasa entero.
- **Revisión humana:** _pendiente_

---

### #17 Informe: mis conclusiones (sección 9.1)

- **Fecha:** 2026-11-18
- **Herramienta y modelo:** Claude Code (extensión de VS Code), Claude Opus 5.5.
- **Prompt clave:** comprobar si estaba hecha mi parte de las conclusiones y, como faltaba, escribirla: 4–6 líneas con un límite real y un aprendizaje de datos, target y features.
- **Qué generó el agente:** el apartado 9.1 de `docs/informe/09-conclusiones.md`, con dos límites (solo resultados y goles, con 185 partidos sin historial; la sensibilidad del target a un gol y la rareza de la clase 4) y dos aprendizajes (la cantidad de datos pesaba más que el modelo; una fuga de datos puede venir del formato de fecha). Solo cambia la línea «Pendiente» de mi apartado, con permiso; el resto del archivo es de Eva y Mariana y no se toca.
- **Comprobación:** las cifras se recalcularon hoy con `download_premier_league_data`, `build_target` y `build_features` sobre las 9 temporadas: 3.420 partidos, 185 sin historial, clase 4 con el 7,9 % y 245 partidos útiles (26 con una temporada), y 80 partidos de 3 goles y 80 de 4 en 2023-24. Los 9 tests que fallan con `<=` son los de la sección 3. No repite lo que ya cuenta Eva en 9.3.
- **Revisión humana:** _pendiente_
