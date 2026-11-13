# Presentación técnica · App, base de datos y despliegue

**Presenta:** Eva · **Duración:** unos 5 minutos (7 diapositivas) · Detalle técnico en [`docs/informe/06-aplicacion-y-despliegue.md`](../informe/06-aplicacion-y-despliegue.md)

---

## 1. Del modelo al producto

**Se ve:** la URL `kiniela-predictor.onrender.com` grande y una captura de la página Predecir con un resultado.

**Se dice:** «Un modelo en un notebook no lo usa nadie. Mi parte lo convierte en un producto: una app web pública donde cualquiera elige un partido y ve qué tipo de resultado esperar. Guarda cada predicción y aprende de lo que dice quien la usa.»

**Captura:** la app con Arsenal – Chelsea predicho (clase y tabla de probabilidades).

---

## 2. Arquitectura

**Se ve:** el diagrama de la sección 6.1 del informe: App → contrato Predictor → modelo / modelo de prueba; App → storage → PostgreSQL → export.

**Se dice:** «La interfaz no tiene lógica: todo vive en `src/kiniela/` y la app solo lo muestra. Eso permite probarlo todo sin abrir la app y no repetir código. Hay tres piezas: predicción, persistencia y exportación para reentrenar.»

---

## 3. El contrato del modelo

**Se ve:**
```python
class Predictor(Protocol):
    version: str
    def predict(self, home_team, away_team) -> list[float]  # 6 probabilidades
```
y un dibujo de un enchufe: la app a un lado, «modelo de prueba» o «modelo final» al otro.

**Se dice:** «Tuve que hacer la app antes de que existiera el modelo. La solución fue un contrato: la app solo exige una versión y seis probabilidades. Hoy usa un modelo de prueba, el reparto real de clases, y lo avisa en pantalla. Cuando llegue el modelo final, se conecta sin tocar la app.»

---

## 4. Feedback y métricas en tiempo real

**Se ve:** captura del formulario «¿Acertó?» y de la página Historial con el acierto.

**Se dice:** «Después de cada predicción, la persona puede decir si acertó y cuál fue la clase real. Con eso medimos el acierto del modelo en producción, por versión, para comparar modelos. Y cada partido con la clase real se exporta con un comando para reentrenar: es el pipeline de recolección de datos que pide el nivel medio.»

**Dato:** `python -m kiniela.storage.export` es incremental, nunca duplica.

---

## 5. Docker

**Se ve:** tabla corta: base slim · requirements separados · sin root · healthcheck · 1,89 GB → 1,23 GB.

**Se dice:** «La app va empaquetada en Docker para que funcione igual en cualquier sitio. Separamos las dependencias de la app de las de desarrollo, la ejecutamos sin privilegios y tiene un healthcheck. Quitando librerías de GPU que no usamos, la imagen bajó un 35 %. Con Docker Compose arranca también un PostgreSQL local, igual que en producción.»

---

## 6. Despliegue: Render + Neon

**Se ve:** el diagrama GitHub → Render → Neon, y `render.yaml`.

**Se dice:** «La app está en Render, que construye nuestro Dockerfile. Los datos van a PostgreSQL en Neon, porque el disco gratuito de Render se borra en cada despliegue. La configuración está en el repo como código, y la contraseña de la base de datos solo como variable de entorno en Render. Lo comprobamos de punta a punta: hicimos una predicción en la web y la vimos guardada en Neon.»

---

## 7. Calidad y límites

**Se ve:** «123 tests en CI · 64 de esta parte · AppTest sin navegador · probado con PostgreSQL real», y abajo los límites.

**Se dice:** «Cada PR pasa 123 tests automáticos; la app se prueba de punta a punta sin navegador. Los límites que conocemos: hasta conectar el modelo final, la app usa el de prueba; el plan gratuito duerme la app tras 15 minutos; y el despliegue es manual. Para cada uno sabemos cómo se resolvería.»

---

## Preguntas probables

| Pregunta | Respuesta corta |
| --- | --- |
| ¿Por qué funciona sin modelo? | Depende de un contrato, no de un modelo concreto; mientras tanto usa un modelo de prueba y lo avisa |
| ¿Dónde están las credenciales? | En la variable de entorno `DATABASE_URL`, solo en el panel de Render. `.env` está en `.gitignore` y en `.dockerignore` |
| ¿Cómo medís el rendimiento en producción? | Con el feedback: acierto = aciertos / predicciones con feedback, por versión de modelo |
| ¿Cómo reentrenaríais? | Export de los partidos con la clase real, unión al histórico, mismas features sin fuga de datos, entrenamiento y promoción si mejora |
| ¿Por qué Neon y no SQLite? | El disco de Render gratis se borra en cada despliegue; Neon gratis persiste y no caduca |
| ¿Por qué no se ejecuta como root? | Por seguridad: si alguien aprovechara un fallo, no tendría permisos de administrador |
