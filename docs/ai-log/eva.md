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
- **Revisión humana:** pendiente en el PR. Puntos a mirar: que `AGENTS.md` refleja lo acordado por el equipo (idioma, ramas y squash), y que la protección de `dev` no exige aprobaciones.
