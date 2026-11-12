# Despliegue

La app está en **Render** (servicio web gratuito, construido desde el `Dockerfile`) y guarda las predicciones en **PostgreSQL de Neon** (plan gratuito).

```text
Persona usuaria ──► Render: contenedor Docker de la app ──► Neon: PostgreSQL
                     (rama dev; main en la entrega)        (predicciones y feedback)
```

**URL pública:** ver el [README](../README.md#despliegue).

## Variables de entorno

| Variable | Dónde | Valor | ¿Secreta? |
| --- | --- | --- | --- |
| `DATABASE_URL` | Render → *Environment* | Cadena de conexión de Neon (`postgresql://…?sslmode=require`) | **Sí**: solo en el panel de Render, nunca en el repo |
| `PORT` | La pone Render | Puerto donde escucha la app; el `Dockerfile` lo lee | No |

Sin `DATABASE_URL`, la app usa SQLite dentro del contenedor, y en Render ese archivo **se borra en cada despliegue**. Por eso en producción es obligatoria.

## Puesta en marcha (una sola vez)

### 1. Base de datos en Neon

1. Entra en [neon.tech](https://neon.tech) con GitHub y crea un proyecto `kiniela`, en la región **Frankfurt** (la misma que Render).
2. En *Connection Details*, copia la cadena de conexión (rol por defecto, base de datos `neondb` o `kiniela`).
3. **No la pegues en ningún archivo ni en el chat.** Solo va en Render (paso 2).

Las tablas se crean solas la primera vez que arranca la app (`init_db`).

### 2. Servicio web en Render

Opción A, con el Blueprint (`render.yaml`):

1. En [render.com](https://render.com), *New* → *Blueprint* y elige el repo `IA-P1-BCN/kiniela-predictor-equipo2`.
2. Render lee `render.yaml`: servicio Docker gratuito en Frankfurt, rama `dev`, healthcheck en `/_stcore/health`.
3. Te pide `DATABASE_URL`: pega la cadena de Neon.

Opción B, a mano, si no se puede conectar la organización de GitHub a Render:

1. *New* → *Web Service* → *Public Git repository*, con la URL `https://github.com/IA-P1-BCN/kiniela-predictor-equipo2`.
2. Rama `dev`, *Runtime* Docker, plan *Free*, región Frankfurt.
3. *Health Check Path*: `/_stcore/health`.
4. *Environment*: añade `DATABASE_URL` con la cadena de Neon.

Conectar Render a una **organización** de GitHub necesita la aprobación de una propietaria de la organización. La opción B evita ese paso porque el repo es público, pero entonces Render no despliega solo en cada push: hay que pulsar *Manual Deploy*.

### 3. Comprobación

1. Abre la URL de Render y haz una predicción.
2. Envía un feedback y mira que sale en **Historial**.
3. Para ver que se ha guardado en Neon: *SQL Editor* → `SELECT * FROM predictions;`.

## Limitaciones del plan gratuito

| Servicio | Qué pasa | Efecto |
| --- | --- | --- |
| Render | El servicio se duerme tras 15 minutos sin visitas | La primera visita tarda alrededor de un minuto en despertar |
| Neon | La base de datos se suspende cuando no se usa | La primera consulta tarda un poco más; la app reconecta sola (`pool_pre_ping`) |

Antes de una demo, conviene abrir la URL un par de minutos antes.

## El modelo en producción

La imagen incluye `models/kiniela_model.joblib` y `models/model_card.json` si están en el repo (ver [contrato del modelo](model-contract.md)). Mientras no exista el modelo entrenado, la app usa el modelo de prueba y lo avisa en pantalla.

## En la entrega: pasar a `main`

1. PR `dev` → `main`. Lo abre otra persona y lo aprueba Eva (`cierre-pr.yml` lo fusiona).
2. En Render, *Settings* → *Branch* → `main` (y en `render.yaml`, `branch: main`).

## En local, igual que en producción

`docker-compose.yml` levanta la app y un PostgreSQL, como Render + Neon:

```bash
docker compose up --build      # http://localhost:8501
docker compose down            # parar; los datos se quedan en el volumen pgdata
docker compose down -v         # parar y borrar la base de datos local
```

En Docker Desktop aparece agrupado como **kiniela**, con los contenedores `app` y `db`.

Si `docker compose build` falla con `failed to execute bake: exit status 1`, es porque Compose pide permiso para leer archivos y la terminal no puede contestar (por ejemplo, la de un agente de IA). Hay dos soluciones: ejecutarlo en una terminal normal y aceptar la pregunta, o lanzar `BUILDX_BAKE_ENTITLEMENTS_FS=0 docker compose build`.
