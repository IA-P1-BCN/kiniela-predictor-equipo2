# Presentación técnica · App, base de datos y despliegue

**Presenta:** Eva · **Duración:** unos 5 minutos (7 diapositivas) más la demo · Detalle técnico en las secciones [6](../informe/06-aplicacion-y-despliegue.md) y [7b](../informe/07b-mlops-feedback-ab.md) del informe · **Estado a 16/11/2026**

---

## 1. Del modelo al producto

**Se ve:** la URL `kiniela-predictor.onrender.com` grande y una captura de la página Predecir con un resultado.

**Se dice:** «Un modelo en un notebook no lo usa nadie. Mi parte lo convierte en un producto: una web pública donde cualquiera elige un partido y ve qué tipo de resultado esperar, con la probabilidad de cada clase. Guarda cada predicción y aprende de lo que dice quien la usa.»

**Captura:** Arsenal – Chelsea predicho, con la tabla de probabilidades y la línea «Predicho con el modelo `tuned-xgb-2026-11-16`».

---

## 2. Arquitectura

**Se ve:** el diagrama de la sección 6.1 del informe: App → contrato `Predictor` → modelo final; App → storage → PostgreSQL → export.

**Se dice:** «La interfaz no tiene lógica: todo vive en `src/kiniela/` y la app solo lo muestra. Así se prueba todo sin abrir la app y no se repite código. Hay tres piezas: predicción, persistencia y exportación para reentrenar.»

---

## 3. El contrato del modelo

**Se ve:**
```python
class Predictor(Protocol):
    version: str
    def predict(self, home_team, away_team) -> list[float]  # 6 probabilidades
```
y un dibujo de un enchufe: la app a un lado, «modelo de prueba» y «modelo final» al otro.

**Se dice:** «Tuve que hacer la app antes de que existiera el modelo. La solución fue un contrato: la app solo exige una versión y seis probabilidades. Con un modelo de prueba pude desplegar desde el primer día. Cuando llegó el modelo final, entró sin tocar la app: calcula las features con la **misma función** que el entrenamiento, para que reciba los mismos datos que aprendió. Antes de publicarlo lo comparé con el modelo de prueba: con una sola temporada no lo superaba, así que lo entrenamos con nueve.»

**Dato:** F1 macro 0,172 frente a 0,080 del modelo de prueba, con 9 temporadas (2015-16 a 2023-24).

---

## 4. Feedback y datos para reentrenar

**Se ve:** captura del formulario «¿Acertó?» y de la página Historial con el acierto y la columna «Modelo».

**Se dice:** «Después de cada predicción, la persona puede decir si acertó y cuál fue la clase real. Cada predicción guarda la versión del modelo, así que medimos el acierto real de cada modelo por separado. Y cada partido con su clase real se exporta con un comando para reentrenar: es el pipeline de recolección de datos que pide el nivel medio.»

**Dato:** `python -m kiniela.storage.export` es incremental: nunca duplica un partido.

---

## 5. A/B testing: cambiar de modelo sin riesgo

**Se ve:** el diagrama de la sección 7b (predicción → reparto → actual o candidato → feedback → regla) y la tabla de las cuatro condiciones.

**Se dice:** «Un modelo nuevo no sustituye al actual porque sí. Responde una parte de las predicciones, la que fijemos con una variable, y un script aplica una regla fija: solo gana si mejora el F1 macro de validación, no sobreajusta, tiene al menos 30 respuestas de feedback y no acierta menos con partidos reales. Si gana, el anterior se archiva para poder volver atrás, y el cambio se publica con un PR revisado.»

**Dato:** regla = F1 +0,01 · gap < 0,05 · 30 feedback por versión · acierto real no menor.

---

## 6. Docker y despliegue: Render + Neon

**Se ve:** el diagrama GitHub → Render (Docker) → Neon, y una tabla corta: imagen slim · sin root · healthcheck · 1,89 GB → 1,23 GB.

**Se dice:** «La app va en Docker para que funcione igual en cualquier sitio: sin privilegios, con healthcheck y sin las librerías de GPU que no usamos, lo que bajó la imagen un 35 %. Render construye esa imagen desde el repo, por eso el modelo final está versionado como excepción. Los datos van a PostgreSQL en Neon, porque el disco gratuito de Render se borra en cada despliegue, y la contraseña solo vive en el panel de Render.»

---

## 7. Calidad y límites

**Se ve:** «212 tests en cada PR · la app probada sin navegador · probado con PostgreSQL real y en Docker», y abajo los límites.

**Se dice:** «Ningún cambio entra en `dev` sin pasar 212 tests automáticos, y la app se prueba de punta a punta sin navegador. Los límites que conocemos: el modelo acierta poco en accuracy porque reparte sus predicciones entre las seis clases; el plan gratuito duerme la app tras 15 minutos; el feedback depende de que la gente lo dé, y nadie verifica la clase real que indica. Para cada uno sabemos cómo se resolvería.»

---

## Demo (2 minutos)

1. **Tres minutos antes**, abrir la web: el plan gratuito tarda alrededor de un minuto en despertar.
2. **Predecir:** «Usar un partido de ejemplo» → «Predecir». Señalar la clase, las 6 probabilidades y la versión del modelo.
3. **Contraste:** Man City – Luton (victoria local clara) y Luton – Man City (gana el visitante).
4. **Feedback:** «No, falló» → clase real → «Enviar feedback».
5. **Historial:** acierto según el feedback y columna «Modelo».
6. **Plan B:** capturas, o en local `docker compose up --build` → http://localhost:8501.

---

## Preguntas probables

| Pregunta | Respuesta corta |
| --- | --- |
| ¿Por qué la accuracy (0,179) es peor que decir siempre «clase 5» (0,318)? | Decir siempre «clase 5» falla todas las demás clases. Medimos con F1 macro, que pesa igual las seis, y ahí el modelo dobla a la referencia (0,172 frente a 0,080). La accuracy baja porque el modelo se atreve con las clases poco frecuentes |
| ¿Por qué 9 temporadas? | Lo medimos: con una, solo 2 de 648 combinaciones cumplían el gap y la mejor no superaba al modelo de prueba. Con 9 lo cumplen 496 y el F1 macro se duplica |
| ¿Cómo sabéis que la app calcula lo mismo que el entrenamiento? | Usa la misma función de features, y un test las compara en todos los partidos reales |
| ¿Por qué el modelo está en git? | Excepción documentada: Render construye la imagen desde el repo, y sin el archivo no llegaría a producción. Son 1,9 MB con su ficha de métricas |
| ¿Dónde están las credenciales? | En la variable de entorno `DATABASE_URL`, solo en el panel de Render. `.env` está en `.gitignore` y en `.dockerignore` |
| ¿Cómo medís el rendimiento en producción? | Con el feedback: acierto = aciertos / predicciones con feedback, por versión de modelo |
| ¿Cómo reentrenaríais? | Export de los partidos con clase real, comprobación de drift, mismas features sin fuga, `python -m kiniela.models.final` y A/B testing frente al actual |
| ¿Por qué Neon y no SQLite? | El disco gratuito de Render se borra en cada despliegue; Neon gratis persiste y no caduca |
| ¿Por qué no se ejecuta como root? | Por seguridad: si alguien aprovechara un fallo, no tendría permisos de administrador |
