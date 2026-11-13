# Informe técnico · Kiniela Predictor, Equipo 2

Informe final del proyecto (issue #17). Cada sección es un archivo, y cada persona escribe la suya en su propio PR: así varios PRs nunca editan el mismo archivo, igual que con las bitácoras de IA.

**Estructura validada por Mariana (13/11/2026).** La propuesta de Eva (PR #44) se acepta. El único cambio es partir la sección 7 en dos archivos, para que Mariana y Eva no editen el mismo documento.

| # | Sección | Archivo | Quién | Estado |
| --- | --- | --- | --- | --- |
| 1 | Problema, objetivo y valor para negocio | [`01-problema.md`](01-problema.md) | Mariana | Escrita |
| 2 | Datos, variable objetivo y EDA | `02-datos-y-eda.md` | Anna | Pendiente |
| 3 | Feature engineering y control de fuga de datos | `03-features.md` | Anna | Pendiente |
| 4 | Modelos, validación, optimización y métricas por clase | `04-modelos-y-metricas.md` | Cala | Pendiente (cuando cierren #7 y #8) |
| 5 | Red neuronal | [`05-red-neuronal.md`](05-red-neuronal.md) | Mariana | Escrita |
| 6 | Aplicación, base de datos y despliegue | [`06-aplicacion-y-despliegue.md`](06-aplicacion-y-despliegue.md) | Eva | Escrita |
| 7a | MLOps: versiones, promoción y data drift | `07a-mlops-flujo-y-drift.md` | Mariana (#16) | Pendiente |
| 7b | MLOps: feedback, reentrenamiento y A/B testing | `07b-mlops-feedback-ab.md` | Eva (#36, #37) | Pendiente |
| 8 | Forma de trabajo: repositorio, CI y uso de IA | [`08-forma-de-trabajo.md`](08-forma-de-trabajo.md) | Eva (borrador; revisamos entre todas) | Borrador |
| 9 | Conclusiones, límites y próximos pasos | `09-conclusiones.md` | Mariana (compila; cada una manda 4–6 líneas) | Pendiente |

## Qué cubre cada sección

1. **Problema y negocio (Mariana).** Kiniela, las 6 clases, para quién es el producto y qué decide una predicción.
2. **Datos y EDA (Anna).** Fuente, temporadas, limpieza, regla de `target` (umbral y precedencia de la clase 5), distribución y conclusiones del EDA.
3. **Features (Anna).** Variables de forma, goles y localía; cómo se evitó la fuga de datos; features de un partido nuevo (#34) si ya está.
4. **Modelos (Cala).** Baseline, ensembles, esquema de validación, overfitting < 5 %, métricas por clase, matriz y errores. Sin números inventados: si #7/#8 no están, se deja el hueco marcado.
5. **Red neuronal (Mariana).** Arquitectura, misma validación que los ensembles, regularización, tabla de comparación.
6. **App (Eva).** Ya escrita.
7a. **MLOps flujo y drift (Mariana).** Cómo se versiona un modelo, cómo se promociona a `kiniela_model.joblib`, umbral PSI y qué hacer si salta la alerta.
7b. **MLOps feedback y A/B (Eva).** Feedback en la app, export incremental (#36) y sustitución A/B (#37) cuando exista.
8. **Forma de trabajo (Eva).** Borrador a revisar: Anna y Cala completan su fila de herramienta de IA.
9. **Conclusiones (Mariana).** Cada persona envía límites y un aprendizaje; Mariana unifica el relato.

## Calendario

| Cuándo | Qué |
| --- | --- |
| **Lunes 16/11** | Cada una tiene el archivo de su sección creado (aunque sea esquema). |
| **Miércoles 18/11, 18:00** | Secciones 1–8 listas para revisión. Cala puede dejar métricas pendientes si #7/#8 no han cerrado, marcadas como «pendiente de cifra». |
| **Jueves 19/11** | Mariana revisa el relato completo (criterio de la #17: que coincida con el producto). Comentarios en el PR o en el tablero. |
| **Viernes 20/11** | Sección 9 unificada + diapositivas finales. |

Si una sección depende de una issue abierta, se escribe igual lo ya hecho y se deja explícito qué falta.

## Normas para escribir una sección

- En español, para alguien técnico que no conoce el proyecto: qué se hizo, **por qué** y con qué resultado.
- Cifras reales y comprobables (métricas, tamaños, número de tests), con la fecha o el commit si pueden cambiar.
- Enlaza el código y la documentación de `docs/` en lugar de copiarlos.
- Los diagramas en bloques `mermaid` se ven directamente en GitHub.
- Un PR por sección, con `Refs #17` (no `Closes`: la issue es de todo el equipo).
- No edites el archivo de otra persona.

## Entregables de la #17

| Entregable | Dónde | Quién cierra |
| --- | --- | --- |
| Informe técnico | Esta carpeta | Cada una su sección; Mariana el relato |
| Presentación técnica | [`docs/presentacion/`](../presentacion/) | Guion en el repo; diapositivas finales en **Canva** |
| Presentación de negocio | [`docs/presentacion-negocio/`](../presentacion-negocio/) | **Mariana** |
| App desplegada | https://kiniela-predictor.onrender.com | Eva |
| Tablero | https://github.com/orgs/IA-P1-BCN/projects/56 | Anna |
