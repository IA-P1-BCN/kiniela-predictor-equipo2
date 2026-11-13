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
- **Revisión humana:** pendiente. Eva revisa el PR antes de fusionarlo.
