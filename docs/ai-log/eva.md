# Bitácora de IA · Eva

| Herramienta | Modelo | Coste | Alcance |
| --- | --- | --- | --- |
| Claude Code (extensión de VS Code) | Claude Opus 5.5 | De pago | Mis tareas: app Streamlit (#9), Docker (#10), base de datos y feedback (#11), despliegue (#12), la CI y la configuración del repo (`.github/`, `AGENTS.md`, `docs/`). El agente redacta el código y estas entradas; yo decido, reviso el diff y hago los commits |

## Entradas

### #21 Puesta en marcha: revisión del backlog, CI con IA y convenciones

- **Fecha:** 2026-11-10
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «clonar el proyecto, enlazarnos al GitHub Project y ver nuestras tareas […] chequea todas las tareas del proyecto y dime si ves algún error o conflicto, si falta alguna tarea […] conectamos Gemini para revisar al hacer los PR, protegemos dev, y los PR nos los podemos aprobar si pasa CI».
- **Qué generó el agente:**
  - La revisión de las 18 issues del Project 56 frente al briefing, con los conflictos y las tareas que faltan:
    - La #9 depende de la #8 y empieza demasiado tarde.
    - No hay CI.
    - `dev` no está protegida.
    - Un test de la #2 se rompe al implementarla.
    - El PR #19 entró directo a `main`.
    - La rama de la #1 queda fuera de `src/kiniela/`.
    - Faltan tareas: CI, pipeline de reentrenamiento, métricas de feedback en tiempo real, A/B testing y sustitución automática del modelo.
  - La propuesta de CI con revisión de Gemini en cada PR y protección de `dev`. Se basa en lo que hicimos en `g2-python-crud-api`, pero escrita de nuevo para este proyecto.
  - Este `AGENTS.md` y la bitácora con un archivo por persona.
  - La issue #21 y su rama `21-ci-ai-review-and-ai-log`.
  - `ci.yml`: ejecuta `pytest` en cada PR y en cada push a `dev`/`main`. Su job `Tests` es el check obligatorio de `dev`.
  - `ai-review.yml` y `.github/scripts/ai_review.py`: Gemini revisa el diff con las reglas de AGENTS.md y deja un único comentario en español. Sin dependencias, sin revisar notebooks (`.ipynb`) y sin bloquear nunca el PR.
  - Dos casillas nuevas en la plantilla de PR: el título en Conventional Commits y la entrada de la bitácora.
- **Aceptado:**
  - Proteger `dev` exigiendo la CI con **0 aprobaciones**, para que cada persona pueda fusionar su PR cuando la CI pase. Gemini solo comenta: no aprueba ni bloquea.
  - Commits y títulos de PR en inglés con Conventional Commits, y fusión con *Squash and merge*.
  - Dejar en español los primeros commits de `dev` y `main`, sin reescribir el historial: hacerlo obligaría a un force-push y rompería la rama de la #1.
  - Un archivo de bitácora por persona, para evitar los conflictos del proyecto anterior.
  - Para la #2: sustituir el test que espera `NotImplementedError` en el mismo PR que implementa `build_target`, con casos límite (2-2, 4-0, 3-1) que fijen la regla.
- **Rechazado o cambiado, y por qué:**
  - Copiar los archivos de `g2-python-crud-api` (AGENTS, workflow, script). Lo usamos solo como referencia y lo escribimos para kiniela, con reglas de ML (fuga de datos, semilla y gap de overfitting).
  - Reescribir con `rebase` y `push --force` los commits en español que ya están subidos.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - Para encontrar «el proyecto con Gemini», el agente empezó a buscar en carpetas de mi disco (`D:\Project1-M2-…`) en vez de preguntar cuál era. Lo paré y le di el repo correcto. Desde entonces lo lee con `gh api`, sin clonarlo.
  - Al principio dio por hecho que podríamos proteger `dev` nosotras. Al comprobar los permisos vio que mi cuenta tiene rol *write*: la protección y el secreto de Gemini los tiene que configurar una admin (Mariana).
  - La primera versión del filtro que quita los notebooks del diff partía el texto por `"\ndiff --git "`. Si el archivo descartado era el primero, el siguiente perdía su cabecera `diff --git`. Se detectó con una prueba local antes del commit y se corrigió partiendo con una expresión regular que conserva cada cabecera.
- **Revisión humana:** Eva revisó el PR #22 y lo fusionó con squash, con `Tests` y la revisión de IA en verde. Puntos mirados: que `AGENTS.md` refleja lo acordado por el equipo (idioma, ramas y squash), y que la protección de `dev` no exige aprobaciones.

### #21 Seguimiento: Gemini en marcha, protección de `dev` y workflow duplicado

- **Fecha:** 2026-11-10
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «aprobemos nuestros PR si están bien y protejamos dev» y «hazlo, cierra el PR, y que pueda mergear».
- **Qué generó el agente:**
  - Volvió a lanzar la revisión de IA del PR #22 tras guardar el secreto, lo fusionó con squash y protegió `dev`: `Tests` obligatorio, 0 aprobaciones, también para admins, y sin force-push ni borrado. El repo queda en squash con el título del PR.
  - Este PR, que borra `.github/workflows/tests.yml`.
  - La actualización de la rama del PR #20 con `dev`, para que reporte el check `Tests` y se pueda fusionar.
- **Aceptado:**
  - Fijar el modelo con la variable del repo `AI_REVIEW_MODEL=gemini-2.5-flash`, sin tocar el código. Para volver al alias basta con borrar la variable.
  - Quedarnos con `ci.yml` y borrar `tests.yml`: los dos creaban un check llamado `Tests`. `tests.yml` instalaba solo `pytest` y habría fallado en cuanto los tests importasen pandas o scikit-learn.
- **Rechazado o cambiado, y por qué:**
  - Dos sugerencias de Gemini sobre `AGENTS.md`: decía que los umbrales de clase están en `config.py`, y no es así (irán en `target.py` con la #2). La métrica del gap de overfitting la fija la #7, que aún no está hecha.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - La primera revisión falló porque el secreto aún no existía. Funcionó como estaba previsto: aviso en el log y check en verde.
  - Con `gemini-flash-latest`, Gemini respondió 503 en cada intento, también tras el reintento. Se resolvió fijando `gemini-2.5-flash`.
  - El agente no sabía que Mariana había subido `tests.yml` directamente a `dev` mientras se preparaba el PR #22. Lo vio al actualizar `dev` en local y comprobar que había dos checks `Tests`.
- **Revisión humana:** Eva, en este PR. Punto a mirar: que después de fusionarlo solo quede un check `Tests` por PR.

### #10 Dockerización y separación de requirements

- **Fecha:** 2026-11-10
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «que nos toca a nosotros, instalaciones docker etc? siguiente tarea», y después «dime que me recomiendas» sobre cómo meter el modelo en la imagen y si separar los requirements.
- **Qué generó el agente:**
  - El `.venv` con Python 3.12.13, la rama `10-dockerize-app` desde la issue y la #10 en «En curso».
  - Un `Dockerfile` nuevo:
    - instala `libgomp1`, que LightGBM necesita;
    - ejecuta la app con un usuario sin privilegios;
    - tiene un `HEALTHCHECK` contra `/_stcore/health` sin curl;
    - usa el puerto de `$PORT` (por defecto 8501) con `exec`, para que `docker stop` llegue a Streamlit;
    - copia de `models/` solo el modelo promocionado y su ficha.
  - Un `.dockerignore` ampliado: secretos, cachés, archivos personales de las IAs y, de `models/`, solo `kiniela_model.joblib` y `model_card.json`.
  - `requirements.txt` (lo que necesita la app para predecir) separado de `requirements-dev.txt` (lo anterior más pytest, matplotlib, seaborn e ipykernel). La CI instala el segundo.
  - El README (instalación y Docker), `AGENTS.md` (comandos, dónde va cada dependencia y cómo conecta cada IA con `AGENTS.md`) y `.gitignore` (`CLAUDE.md`, `GEMINI.md` y los ajustes locales son personales).
- **Aceptado:**
  - Separar los requirements: la imagen solo lleva lo necesario para predecir, como pide el briefing («un requirements.txt limpio»).
  - Para el despliegue (#12), versionar en git solo el modelo final y su `model_card.json`, sin volúmenes ni descargas. Queda por acordar con Cala, que genera el artefacto.
  - Quitar de la imagen las librerías NVIDIA NCCL que instala XGBoost para entrenar con varias GPU: la app predice con CPU. La imagen baja de 1,89 GB a 1,23 GB, y XGBoost y LightGBM siguen funcionando.
  - Cada persona tiene su `CLAUDE.md` o `GEMINI.md` fuera de git, con `@AGENTS.md` para cargar las reglas comunes.
- **Rechazado o cambiado, y por qué:**
  - Instalar `jupyter` completo: basta `ipykernel`, que es lo que usa VS Code para los notebooks.
  - Cambiar a `xgboost-cpu` en `requirements.txt`: afectaría al entorno de todo el equipo y no tiene versión para macOS. El recorte se hace solo dentro de la imagen.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - El primer `CMD` en forma shell provocaba el aviso `JSONArgsRecommended`: Streamlit no recibía la señal de parada. Se cambió a `["sh", "-c", "exec …"]`, que mantiene `$PORT`.
  - El primer intento de quitar NCCL desinstalaba `nvidia-nccl-cu12`, pero el paquete instalado era `cu13`. `pip uninstall` no da error si el paquete no existe, así que la imagen seguía igual. Se detectó porque el tamaño no bajó al revisar las capas con `docker history`, y se cambió por un filtro que encuentra cualquier `nvidia-nccl-*`.
- **Pruebas:** `docker build` sin avisos. `docker run` responde 200 y sale `healthy`, también con `PORT=8080`. El usuario es `appuser`, en la imagen no hay `.env`, datos, tests ni pytest, y `docker stop` tarda menos de 1 s. `pytest` pasa en local.
- **Revisión humana:** pendiente en el PR.

### #11 Base de datos de predicciones y feedback

- **Fecha:** 2026-11-10
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «ok» a empezar la #11. El agente propuso el diseño y preguntó dos decisiones: la librería y la base de datos de producción.
- **Qué generó el agente:**
  - `src/kiniela/storage/`:
    - conexión con `DATABASE_URL` (SQLite por defecto, PostgreSQL en Neon en producción);
    - las tablas `predictions` y `feedback`;
    - las funciones `save_prediction`, `save_feedback`, `list_history` y `feedback_stats`, esta última con el acierto por versión de modelo para las métricas en tiempo real.
  - 24 tests nuevos con SQLite temporal (30 en total).
  - `docs/database.md` con el esquema, el porqué de cada columna y consultas útiles; `.env.example`; README y `AGENTS.md`.
  - En la imagen Docker, una carpeta `data/` escribible por `appuser`.
- **Aceptado:**
  - SQLAlchemy 2 y PostgreSQL en Neon (decisiones de Eva): el mismo código sirve en local y en producción, y la base de datos gratuita de Neon no caduca, a diferencia de la de Render (30 días).
  - Las probabilidades en 6 columnas (se agregan en SQL) y las entradas en JSON (las features de la #3 pueden cambiar sin tocar la tabla).
  - `model_version` en cada predicción, para el A/B testing y la #16.
  - `predicted_class` se calcula a partir de las probabilidades con la misma función que usa la app (`predicted_class`), sin duplicar la validación.
  - Un feedback por predicción, y `actual_class` tiene que cuadrar con `is_correct`.
  - Las funciones del repositorio no confirman la transacción: lo hace `session_scope`, que deshace todo si algo falla.
- **Rechazado o cambiado, y por qué:**
  - `sqlite3` de la librería estándar: solo vale para SQLite, y en Render gratis el archivo se borra en cada despliegue.
  - La base de datos de Render (caduca) y MongoDB (cambiaría el diseño).
  - Migraciones con Alembic: de momento `init_db` crea las tablas. Se añadirán si el esquema cambia.
- **Errores o alucinaciones del agente y cómo se corrigieron:** ninguno en esta tarea. Como los tests usan SQLite, el agente probó también contra un PostgreSQL 17 real en Docker: el driver psycopg, el JSON, las fechas en UTC y el rechazo de clases fuera de rango y de feedback sin predicción.
- **Revisión humana:** pendiente en el PR.
