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
- **Revisión humana:** pendiente. Eva revisa el PR antes de fusionarlo.
