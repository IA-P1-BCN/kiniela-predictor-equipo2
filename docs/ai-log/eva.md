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
- **Revisión humana:** Eva fusionó el PR #24 con `Tests` y la revisión de IA en verde. Gemini señaló como problema que `COPY app` iba antes que `COPY src`, y era al revés: una alucinación que no se aplicó. Ejemplo de por qué su revisión solo orienta.

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
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - En el código, ninguno. Como los tests usan SQLite, el agente probó también contra un PostgreSQL 17 real en Docker: el driver psycopg, el JSON, las fechas en UTC y el rechazo de clases fuera de rango y de feedback sin predicción.
  - En el proceso: el PR #25 decía `Refs #11` para dejar la issue abierta hasta tener la interfaz, pero la #11 se cerró sola al fusionar. La rama se había creado con `gh issue develop`, que la enlaza a la issue, y GitHub cierra la issue enlazada al fusionar en la rama por defecto aunque no haya `Closes`. Se reabrió con un comentario. Para trabajo parcial hay que usar una rama sin enlazar.
- **Revisión humana:** Eva fusionó el PR #25 con `Tests` y la revisión de IA en verde. Las sugerencias de Gemini no se aplicaron: el `chown` de `data/` en la imagen no puede fallar porque `appuser` se crea en esa misma capa, y pasar las probabilidades a `Numeric` no aporta nada.

### #9 Aplicación Streamlit (cierra también la #11)

- **Fecha:** 2026-11-11
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «ok» a empezar la #9. El agente propuso el diseño y preguntó dos decisiones: qué modelo de prueba usar sin modelo entrenado y de dónde sacar los equipos.
- **Qué generó el agente:**
  - La app con dos páginas (`st.navigation`):
    - **Predecir:** equipos o partido de ejemplo, la clase predicha con su nombre, una tabla con las 6 probabilidades, el guardado en la base de datos y el formulario de feedback (acertó o falló, la clase real y un comentario).
    - **Historial:** las últimas 50 predicciones con su feedback, y el acierto en tiempo real del modelo actual y de todos.
  - En `src/`:
    - el contrato `Predictor` (`version` + `predict(home, away)` → 6 probabilidades);
    - `ReferencePredictor`, el modelo de prueba con las frecuencias de clase;
    - `load_predictor()`, que usa `models/kiniela_model.joblib` si existe;
    - `validate_teams()`, compartida por la app y la base de datos;
    - `kiniela/data/catalog.py`, con los equipos y los targets del dataset, y valores de respaldo si no hay datos.
  - 46 tests nuevos (76 en total). Los de la app usan `AppTest` de Streamlit, sin navegador: predicción, entradas inválidas, feedback e historial.
  - `docs/model-contract.md` para quien entregue el modelo, más README y `AGENTS.md`.
- **Aceptado:**
  - Modelo de prueba con frecuencias de clase (decisión de Eva): es honesto, la app lo avisa en pantalla y no invade el trabajo de modelado.
  - Equipos sacados del dataset procesado, con la lista de la Premier 2023-24 como respaldo (decisión de Eva). Dentro de Docker no hay `data/`, y la app tiene que funcionar igual.
  - La app solo conoce el contrato `Predictor`. Cuando Cala entregue el modelo, la app no se toca.
  - La validación de equipos sale de `src/` y se usa en la app y en la base de datos, sin duplicarla. La app traduce los mensajes al español.
  - Si la base de datos falla, la predicción se muestra igualmente, con un aviso.
- **Rechazado o cambiado, y por qué:**
  - Un modelo de Poisson como modelo de prueba: queda mejor en una demo, pero es trabajo de modelado (#5–#8).
  - Equipos en texto libre: los errores de escritura no los reconocería el modelo real.
  - Hacer una página nueva para el feedback de partidos antiguos: de momento el feedback se da justo después de predecir.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - Los tests de la app fallaban porque `AppTest.from_file` busca las rutas relativas desde el archivo del test, no desde la raíz. Se pasó una ruta absoluta.
  - Tres tests fallaban porque, con una entrada inválida, la app no llega a abrir la base de datos y las tablas no existían cuando el test las leía. El fallo estaba en el test, no en la app, y se corrigió creando las tablas en el helper del test.
  - El agente usó `use_container_width`, que en local no avisaba. Dentro de Docker, Streamlit avisó de que se retira después del 31/12/2025, una fecha ya pasada. Se cambió a `width="stretch"` y se subió el mínimo a `streamlit>=1.50`.
  - Un heredoc de bash con comillas en el contenido falló al escribir los tests. Se escribieron con el editor, sin pasar por el shell.
- **Pruebas:** `pytest` (76 tests). La app arrancada en local responde 200. Dentro de la imagen Docker, sin `data/`, salen los 20 equipos de respaldo y se ejecuta el flujo completo con `AppTest`: predicción e historial, sin errores ni avisos.
- **Revisión humana:** Eva probó la app en el navegador y fusionó el PR #27 con `Tests` y la revisión de IA en verde. Las sugerencias de Gemini eran menores y no se aplicaron: la tupla de respaldo es inmutable a propósito, y el modelo en caché se recarga reiniciando la app.

### #12 Despliegue (parte 1: configuración y Compose)

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «ok» a empezar la #12. El agente preguntó dos decisiones: desde qué rama desplegar y si añadir Docker Compose.
- **Qué generó el agente:**
  - `render.yaml` (Blueprint de Render): servicio Docker gratuito en Frankfurt, rama `dev`, healthcheck en `/_stcore/health` y `DATABASE_URL` como secreto que solo se rellena en el panel.
  - `docker-compose.yml`: la app con PostgreSQL 17, igual que en producción, como proyecto `kiniela` en Docker Desktop.
  - `docs/deploy.md`: los pasos de Neon y Render, las variables, las limitaciones del plan gratuito y cómo pasar a `main`. Además, el README y `.env.example`.
  - En `AGENTS.md`, una lista de comprobación obligatoria para los PRs, después de que tres PRs entraran con el título y la descripción sin rellenar y uno vacío.
- **Aceptado:**
  - Desplegar desde `dev` ahora y pasar a `main` en la entrega (decisión de Eva): `main` va 12 commits por detrás y no tiene la app.
  - Añadir Compose (decisión de Eva).
  - Conectar Render por la URL pública del repo: conectar la organización IA-P1-BCN necesita a una propietaria. El precio es que cada despliegue se lanza a mano.
  - Conexión directa a Neon, sin pooler: psycopg 3 usa *prepared statements*, que pueden fallar a través del pooler.
- **Rechazado o cambiado, y por qué:**
  - El prompt de configuración que propone Neon para agentes: está pensado para Node.js (`npm`, `neon.ts`, `npm run build`). Habría llenado el repo de archivos de Node y escrito credenciales en un `.env.local`. La app ya lee `DATABASE_URL`.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - `docker compose build` falló con `failed to execute bake: exit status 1`. Compose 5 pide permiso para leer archivos, y la terminal del agente no puede contestar. Se confirmó con `BUILDX_BAKE_ENTITLEMENTS_FS=0` y se documentó en `docs/deploy.md`.
  - El agente lanzó la prueba del Compose con Docker Desktop apagado, y un bucle de espera sin límite se quedó colgado hasta pararlo a mano. Los bucles siguientes llevan un número máximo de intentos.
- **Pruebas:** con Compose, la app y la base de datos salen *healthy*, y la predicción hecha desde la app queda guardada en PostgreSQL. `pytest` pasa.
- **Revisión humana:** Eva fusionó el PR #32 con `Tests` en verde. Gemini afirmó que el PR no añadía una entrada nueva a la bitácora, y sí la añadía (esta). No se aplicó.

### #12 Despliegue (parte 2: app en producción)

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** las capturas de Neon y Render que Eva iba compartiendo, y la URL desplegada. El agente guió los pasos en los paneles, que hizo Eva.
- **Qué hizo Eva en los paneles:**
  - Un proyecto en Neon con la conexión directa, sin pooler.
  - Un Blueprint `kiniela` en Render con la URL pública del repo y la rama `dev`.
  - `DATABASE_URL` pegada solo en Render.
- **Qué generó el agente:** la URL pública y el enlace al tablero en el README, en lugar de la frase antigua de que el repo no tenía modelo.
- **Aceptado:**
  - Desplegar por la URL pública del repo: no hace falta que una propietaria de la organización apruebe la app de Render. A cambio, cada despliegue se lanza a mano (*Manual Deploy*).
  - No usar el prompt para agentes de Neon (era para Node.js).
- **Rechazado o cambiado, y por qué:** nada.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - Se repitió lo de la #11: la rama de la parte 1 estaba enlazada a la #12 y la issue se cerró sola al fusionar el PR #32 con `Refs`. Esta vez estaba previsto y se reabrió en el momento.
  - El agente no puede manejar el navegador, así que la prueba de punta a punta en la URL pública la hizo Eva. El agente comprobó el healthcheck (`ok`) y la respuesta HTTP 200.
- **Pruebas:**
  - En https://kiniela-predictor.onrender.com: predicción Arsenal – Chelsea (clase 5, 6 probabilidades), sin aviso de base de datos, y feedback guardado.
  - Para confirmar que se guarda en Neon y no en un SQLite temporal del contenedor, Eva consultó `predictions` con su `feedback` en el SQL Editor de Neon. Salió la fila: `arsenal`, `chelsea`, clase 5, `is_correct = t`, `actual_class = 5`.
- **Revisión humana:** Eva, en el navegador y en Neon. Fusionó el PR #33 con `Tests` en verde; Gemini no encontró problemas.

### #36 Pipeline de datos para reentrenamiento

- **Fecha:** 2026-11-12
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:**
  - «y nos queda alguna tarea? y al resto que le falta». El agente detectó cuatro tareas necesarias sin issue y comprobó cuáles salen literalmente del briefing.
  - «las 4 issues nuevas están en los requisitos del briefing? […] creamos las tareas y las dejamos sin dueño […] asígnanos la del pipeline». Se crearon las #34, #35 y #37 sin dueña y la #36 para Eva.
- **Qué generó el agente:**
  - `src/kiniela/storage/export.py`: exporta a CSV las predicciones con feedback y clase real, con un comando `python -m kiniela.storage.export` y los filtros `--since` y `--model-version`.
  - 8 tests nuevos (99 en total).
  - `docs/retraining.md`: cómo ejecutarlo, qué columnas exporta, cómo se usa para reentrenar y qué precauciones tener. Enlaces en el README y una línea en `AGENTS.md`.
- **Aceptado:**
  - **Export incremental** comparando con el `prediction_id` que ya hay en el CSV, en vez de añadir una columna `exported_at` a la base de datos. Sin migraciones, `init_db` no añade columnas a tablas que ya existen, así que habría roto la base de datos de Neon.
  - Solo se exporta el feedback **con clase real**: un «falló» sin clase no es una etiqueta.
  - Las columnas siguen el dataset histórico (`HomeTeam`, `AwayTeam`, `Date`), y la etiqueta se llama `target`, importada de `kiniela.models.train`, para no repetir el nombre. Así las features se recalculan con el mismo pipeline, sin fuga de datos.
  - La salida va a `data/raw/feedback/`, que no se versiona.
  - Para producción, `DATABASE_URL` se carga desde `.env` en la terminal. Nunca como argumento, porque quedaría en el historial.
- **Rechazado o cambiado, y por qué:**
  - Exportar las `inputs` en JSON: ahora solo llevan los equipos, y las features se recalculan desde el historial.
  - Que el export lance el reentrenamiento: es trabajo de las #35 y #37.
- **Errores o alucinaciones del agente y cómo se corrigieron:**
  - El filtro `--since` comparaba una fecha sin zona horaria con fechas guardadas en UTC. En SQLite funcionaba, pero en PostgreSQL podía desplazar el corte. Se cambió a medianoche UTC y se probó contra PostgreSQL.
  - Un test incluía una comprobación que no probaba nada (el nombre de la tabla). Se quitó.
  - Para probar en el contenedor del Compose, `docker compose exec -w /app` falló porque Git Bash convierte `/app` en una ruta de Windows. Se resolvió con `MSYS_NO_PATHCONV=1`.
- **Pruebas:**
  - `pytest`: 99 tests.
  - Contra el PostgreSQL del Compose: la primera ejecución exporta 1 partido, la segunda 0 (sin duplicados), y `--since` filtra bien.
- **Revisión humana:** Eva fusionó el PR #38 con `Tests` en verde. Gemini no encontró problemas; sugirió un comentario sobre `Date` en el código, que ya estaba explicado en `docs/retraining.md`.

### Revisión de PRs del equipo (12 y 13/11)

- **Fecha:** 2026-11-12 y 2026-11-13
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «chequea el PR de Mariana y ciérralo con mensaje si está ok».
- **Qué hizo el agente:**
  - Revisó y fusionó, con un comentario de Eva, los PRs de Mariana #41 (red neuronal, #13) y #42 (data drift con PSI, #14). Antes comprobó la validación cruzada, la ausencia de fuga de datos (escalado dentro de cada fold), los casos límite del PSI y la lista de comprobación de PR.
  - Asignó la #34 a Anna.
  - Detectó que el PR #43 de Anna, fusionado y titulado como corrección de features, solo cambiaba su bitácora, sin código. Preparó un mensaje privado para que lo rehaga.
- **Errores o alucinaciones:** Gemini dijo que en el #41 había un import duplicado. Era cierto a medias: no se repetía nada, pero había dos imports del mismo módulo. Se comprobó en el código antes de comentarlo.
- **Revisión humana:** Eva decidió fusionar y comentar.

### #17 Informe técnico y guion: sección de app y despliegue

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «ok» a adelantar nuestra parte de la #17. El agente preguntó cómo organizar el informe (compartido por las cuatro) y qué preparar para la presentación.
- **Qué generó el agente:**
  - `docs/informe/README.md`: propuesta de estructura en 9 secciones, un archivo por sección con su responsable, para que Mariana la valide.
  - `docs/informe/06-aplicacion-y-despliegue.md`: arquitectura, contrato del modelo, base de datos, export, Docker, despliegue, calidad y límites.
  - `docs/informe/08-forma-de-trabajo.md`: borrador sobre flujo, CI, Gemini y uso de la IA, para revisar entre todas.
  - `docs/presentacion/`: guion de 7 diapositivas de nuestra parte, con lo que se ve, lo que se dice y las preguntas probables.
  - Enlaces en el README.
- **Aceptado:**
  - Un archivo por sección (decisión de Eva), por la misma razón que las bitácoras: dos PRs nunca editan el mismo archivo.
  - Un guion en Markdown en lugar de diapositivas (decisión de Eva), para pasarlo a la herramienta que elija el equipo.
  - Rama **sin enlazar** a la #17 y `Refs #17`: la issue es de todo el equipo y no debe cerrarse con este PR.
- **Rechazado o cambiado, y por qué:** crear los archivos vacíos de las otras secciones. Cada persona crea el suyo; el índice dice cuál es.
- **Errores o alucinaciones del agente y cómo se corrigieron:** el primer borrador decía que 63 tests cubrían esta parte. Se contaron con `pytest --collect-only` y son 64; se corrigió antes del commit.
- **Revisión humana:** pendiente en el PR. Mariana tiene que validar la estructura del informe.

### #37 A/B testing y promoción automática del modelo

- **Fecha:** 2026-11-13
- **Herramienta y modelo:** Claude Code, Claude Opus 5.5.
- **Prompt clave:** «asígnanos la 37» y «ok» al plan. El agente preguntó qué regla de promoción usar y cómo repartir las predicciones entre los dos modelos.
- **Qué generó el agente:**
  - `src/kiniela/models/ab_testing.py`: reparto aleatorio por predicción entre el modelo actual y un candidato (`AB_CANDIDATE_SHARE`), lectura de las fichas `model_card.json`, evidencia por versión (validación + feedback) y la regla `should_promote`.
  - `src/kiniela/models/promote.py`: script `python -m kiniela.models.promote [--dry-run]` que decide y, si el candidato gana, archiva el modelo actual en `models/archive/<versión>/`.
  - App: la página Predecir usa el reparto y guarda la versión que ha respondido; el Historial muestra la tabla de comparación cuando hay candidato.
  - 37 tests nuevos (regla con casos fijos, reparto, script y app de punta a punta). La suite pasa de 123 a 160.
  - `docs/ab-testing.md`, y referencias en el contrato del modelo, el despliegue, el README, `.env.example` y `.dockerignore`.
- **Aceptado:**
  - Regla F1 macro + feedback (decisión de Eva): F1 macro de validación ≥ actual + 0,01, gap < 0,05, al menos 30 predicciones con feedback por versión y acierto real no menor. Umbrales como constantes, por si el equipo acuerda otros.
  - Reparto aleatorio por predicción (decisión de Eva), que reparte el tráfico en la proporción pedida.
  - El script decide y cambia los archivos, pero publicar pasa por PR y *Manual Deploy*: en Render el modelo va dentro de la imagen y un cambio en el contenedor se perdería sin revisión.
- **Rechazado o cambiado, y por qué:** nada rechazado. Al probarlo, el agente vio que sin candidato el script acababa con un *traceback*; lo cambió por un mensaje claro y código de salida 1.
- **Errores o alucinaciones del agente y cómo se corrigieron:** al editar el script con un *heredoc*, un `\n` se convirtió en un salto de línea real y rompió el f-string; lo detectó la suite antes del commit. Al probar el comando se vio que `python -m kiniela...` necesita `PYTHONPATH=src`; en esta guía se documentó así.
- **Revisión de Gemini:** señaló que el reparto no usaba `RANDOM_STATE`. Se aceptó: el router se crea con esa semilla y un test comprueba que el reparto es reproducible. Se descartó su sugerencia de un mensaje más visible para el modelo de prueba, porque el script ya lo explica.
- **Revisión humana:** Eva aprobó la regla y los umbrales; fusionado con *Squash and merge* (PR #48).
