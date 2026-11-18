# Bitácora de IA · Mariana

| Herramienta | Modelo | Coste | Alcance |
| --- | --- | --- | --- |
| Cursor | Grok 4.7 | Incluido en la suscripción | Issue #13, red neuronal |

### #13 Red neuronal

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «arranca mi parte». La parte de Mariana es MLOps: se empezó por la issue #13 porque datos, baseline y ensembles ya estaban cerrados.
- **Qué generó el agente:** `src/kiniela/models/neural.py` y `tests/test_neural.py`. Red MLP de scikit-learn, sin dependencia nueva, con la misma validación que los ensembles, L2 y early stopping.
- **Aceptado:** el código y los tests de esta entrada, pendientes de revisión humana del PR.
- **Rechazado o cambiado, y por qué:** no se añadió TensorFlow: el repo pide no meter dependencias que la issue no exija, y scikit-learn ya está.
- **Errores o alucinaciones del agente y cómo se corrigieron:** el clon local estaba atrasado respecto a `dev`. Se trabajó sobre el `dev` actual, no sobre la base vieja.
- **Revisión humana:** fusionada en `dev` (PR #41).

### #14 Data drift

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «podemos seguir» después de fusionar la red neuronal.
- **Qué generó el agente:** PSI en `src/kiniela/monitoring/drift.py`, tests, `docs/drift.md` y enlace en el README. Umbral 0.20 por feature y a nivel global.
- **Aceptado:** el código y los tests de esta entrada, pendientes de revisión humana del PR.
- **Rechazado o cambiado, y por qué:** no se usó Kolmogorov–Smirnov como criterio de corte; el PSI deja un umbral único y comparable por feature.
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno en esta tarea.
- **Revisión humana:** fusionada en `dev` (PR #42).

### #17 Coordinación del informe y las presentaciones

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** mensaje de Claudio/Eva pidiendo validar la estructura de `docs/informe/` y repartir.
- **Qué generó el agente:** README validado, sección 7 partida en 7a/7b, esquemas de cada archivo, presentación de negocio, calendario.
- **Aceptado:** el reparto y las fechas de este PR, para que el equipo pueda escribir sin chocar.
- **Rechazado o cambiado, y por qué:** no se dejó la sección 7 en un solo archivo (conflicto entre Mariana y Eva). Presentación técnica: una persona por parte, no «Anna / Mariana».
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** fusionada en `dev` (PR #45).

### #16 Documentación MLOps

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «hazlo»: fusionar la estructura del informe y seguir con #16 y #15.
- **Qué generó el agente:** `docs/mlops.md` (versiones, promoción, feedback, drift y alerta) y la sección 7a del informe.
- **Aceptado:** el documento operativo; el detalle de export y A/B se enlaza a Eva (7b), no se duplica.
- **Rechazado o cambiado, y por qué:** no se inventó un cron de drift; el comando se lanza cuando hay lote nuevo.
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** fusionada en `dev` (PR #46).

### #15 Tests unitarios

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «hazlo» — cerrar #15 junto con #16.
- **Qué generó el agente:** `kiniela.data.validate`, `kiniela.models.metrics` y tests de esquema, nulos, rangos, `target` 0-5, forma de la predicción y un caso de métricas con resultado conocido.
- **Aceptado:** esos módulos y tests. No se duplicó lo que ya cubrían `test_target.py` y `test_predict.py`.
- **Rechazado o cambiado, y por qué:** no se tocó la suite existente para «hacer sitio»; se añadieron archivos.
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** fusionada en `dev` (PR #47).

### #15 Recálculo con 8 features (16/11)

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** Claudio: las features son 8 (#58/#61); actualizar la rama contra `dev`.
- **Qué generó el agente:** `FEATURES` de los tests apunta a `FEATURE_COLUMNS`; drift y red usan esos nombres.
- **Aceptado:** tests sintéticos con las 8 columnas reales.
- **Rechazado o cambiado, y por qué:** no se entrenó la red sobre el CSV real en este PR (eso va en la sección 5 / #53).
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** fusionada en `dev` (PR #47).

### #17 Secciones 1, 5 y guiones

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «levantalo» — redactar el informe de Mariana y los guiones.
- **Qué generó el agente:** `01-problema.md`, `05-red-neuronal.md`, guion de negocio y diapositivas técnicas 4.
- **Aceptado:** el texto. No se inventaron F1 ni accuracy: quedan huecos para el run oficial y para Carla.
- **Rechazado o cambiado, y por qué:** no se fusionaron #46 y #47 desde aquí (el merge pidió autorización y caducó).
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** pendiente en #53.

### #47/#53 Revisión de Claudio (16/11)

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** conflictos con `dev`; 8 features; `promote`; modelo en git; Carla; 7b escrita.
- **Qué generó el agente:** merge con `dev`, `docs/mlops.md` y 7a alineados con #37/#35, sección 5 sin cifras viejas y tabla-hueco, Cala→Carla en archivos de Mariana.
- **Aceptado:** el recálculo de la red queda como comando a relanzar, no como números inventados.
- **Rechazado o cambiado, y por qué:** no se editaron bitácoras ajenas ni la sección 8 de Eva.
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno.
- **Revisión humana:** #47 en `dev`; #53 se reabre contra `dev` tras el squash.

### #53 Recálculo de la red con 8 features (16/11)

- **Fecha:** 2026-11-16
- **Herramienta y modelo:** Cursor, Grok 4.7
- **Prompt clave:** «sigue» — rellenar la tabla de la sección 5 con el CSV actual.
- **Qué generó el agente:** features + `target` desde `premier_league_2023_24.csv` y `python -m kiniela.models.neural`; tabla de 5.3 con las cifras de ese run.
- **Aceptado:** las métricas de ese comando, no las de 11 features.
- **Rechazado o cambiado, y por qué:** el CSV de modelado no se commitea; se genera al vuelo.
- **Errores o alucinaciones del agente y cómo se corrigieron:** el merge de #47 dejó conflicto otra vez en esta bitácora; se unieron las entradas de #15 y #17.
- **Revisión humana:** pendiente en #53.

### Auditoría de código en `dev` (18/11)

- **Fecha:** 2026-11-18
- **Herramienta y modelo:** Cursor, Grok 4.6
- **Prompt clave:** «realizame una auditoria de codigo» y luego «arreglalo».
- **Qué generó el agente:** tope de 20 predicciones por sesión; `predicted_at` en el export (ya no se finge `Date` de partido); selectores = `predictor.teams`; Render exige `DATABASE_URL`; caps de versiones y LightGBM solo en dev; CODEOWNERS del `.joblib`.
- **Aceptado:** los must-fix y should-fix que cabían sin migrar Neon ni reescribir el pickle.
- **Rechazado o cambiado, y por qué:** no Alembic (no hay columna nueva); el límite es por sesión, no por IP.
- **Errores o alucinaciones del agente y cómo se corrigieron:** el clone local estaba en `main` viejo; se trabajó sobre `origin/dev`.
- **Revisión humana:** este PR.
