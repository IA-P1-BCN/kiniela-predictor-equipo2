# 9. Conclusiones, límites y próximos pasos

**Quién:** Mariana compila · **Aportan:** Anna, Carla, Eva, Mariana · **Estado a 18/11/2026** (entrega: 18/11, 23:59)

Cada persona escribe su entrada en su apartado: **4–6 líneas**, con un límite real y un aprendizaje de su parte. Mariana une el relato al final.

## 9.1 Anna · Datos, target y features

*Pendiente: la escribe Anna.*

## 9.2 Carla · Modelos y métricas

*Pendiente: la escribe Carla.*

## 9.3 Eva · App, base de datos, despliegue y MLOps

- **Límite:** el modelo está fijo desde el 16/11 y el feedback depende de la gente. Hoy hay muy pocas respuestas y nadie verifica la clase real, así que el acierto en tiempo real todavía no dice nada. Próximo paso: rellenar la clase real con los resultados oficiales de la misma fuente y reentrenar con el proceso que ya existe (export, drift, A/B testing y promoción con regla fija).
- **Límite:** la app vive en el plan gratuito de Render (se duerme tras 15 minutos) y el despliegue es manual. Suficiente para el proyecto; para un uso real haría falta un plan de pago y despliegue automático.
- **Aprendizaje:** un contrato entre la app y el modelo (`Predictor`) permitió desplegar desde el primer día con un modelo provisional y conectar el modelo final sin tocar la app.
- **Aprendizaje:** el contrato no basta. La app calculaba las features distinto que el entrenamiento, y lo descubrimos comparando con partidos reales, no con tests. Desde entonces una sola función y un test lo garantizan.
- **Aprendizaje:** medir antes de publicar. Con una temporada, el modelo optimizado no superaba al provisional; con nueve, el F1 macro se dobló (0,172 frente a 0,080). Y los tests deben ejecutarse con las mismas dependencias que producción: en el PR #77, quitar LightGBM del runtime habría roto la carga del modelo con el CI en verde.

## 9.4 Mariana · Red neuronal, MLOps y producto

*Pendiente: la escribe Mariana.*
