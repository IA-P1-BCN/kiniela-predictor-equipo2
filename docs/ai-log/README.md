# Bitácora de IA

Registro de cómo usa la IA cada persona del equipo: qué herramienta y modelo, qué se le pidió, qué se aceptó, qué se rechazó y en qué se equivocó el agente.

## Un archivo por persona

| Persona | Archivo |
| --- | --- |
| Anna | [anna.md](anna.md) |
| Cala | [cala.md](cala.md) |
| Eva | [eva.md](eva.md) |
| Mariana | [mariana.md](mariana.md) |

**Por qué un archivo por persona:** en el proyecto anterior la bitácora era un solo archivo y cada PR añadía su entrada al final. Dos PRs abiertos a la vez tocaban las mismas líneas, salían conflictos en casi todos y alguna entrada se perdió al resolverlos. Con un archivo por persona, dos PRs nunca editan el mismo archivo.

## Reglas

- Cada persona escribe **solo en su archivo**. Si aún no existe, lo crea en su primer PR con la cabecera de abajo.
- Una entrada por tarea o PR, **en el mismo PR** que el cambio.
- Las entradas van en orden cronológico: la más nueva, al final de tu archivo.
- Este README solo se toca para cambiar la plantilla o las reglas.

## Cabecera de cada archivo

```markdown
# Bitácora de IA · <Nombre>

| Herramienta | Modelo | Coste | Alcance |
| --- | --- | --- | --- |
| | | | |
```

## Plantilla de entrada

```markdown
### #<issue> <título corto>

- **Fecha:** AAAA-MM-DD
- **Herramienta y modelo:**
- **Prompt clave:** lo que se le pidió al agente, resumido o literal.
- **Qué generó el agente:**
- **Aceptado:**
- **Rechazado o cambiado, y por qué:**
- **Errores o alucinaciones del agente y cómo se corrigieron:**
- **Revisión humana:** quién revisó el PR y qué miró.
```
