# 9. Conclusiones, límites y próximos pasos

**Quién:** Mariana compila · **Aportan:** Anna, Carla, Eva, Mariana · **Estado a 18/11/2026** (entrega: 18/11, 23:59)

Cada persona escribe su entrada en su apartado: **4–6 líneas**, con un límite real y un aprendizaje de su parte. Mariana une el relato al final.

## 9.1 Anna · Datos, target y features

- **Límite:** solo usamos resultados y goles de la Premier League. No hay lesiones, alineaciones, descanso entre partidos ni cuotas, y el historial se reinicia en cada temporada. Por eso las primeras jornadas no se pueden predecir: se descartan 185 de 3.420 partidos. Próximo paso: aprovechar la forma de la temporada anterior y añadir variables que se conocen antes del partido, como el descanso.
- **Límite:** la regla del target es muy sensible a un gol: en 2023-24 hubo 80 partidos de 3 goles y otros 80 de 4. Además, la clase 4 sigue siendo la más rara (7,9 %, 245 partidos útiles), así que es la que peor se aprende.
- **Aprendizaje:** el problema era la cantidad de datos más que el modelo. Con una temporada había 26 partidos útiles de la clase 4; con nueve, 245, y fue lo que permitió que el modelo final superara al provisional.
- **Aprendizaje:** una fuga de datos puede venir de algo tan pequeño como el formato de fecha. Ordenar `dd/mm/aaaa` como texto metía partidos futuros en el «pasado», y la temporada 2016-17 trae el año con dos cifras. Ahora las fechas se convierten antes de ordenar, y si se vuelve a meter la fuga fallan 9 tests.

## 9.2 Carla · Modelos y métricas

*Redactada por Eva el 18/11 a partir de la [sección 4](04-modelos-y-metricas.md), a falta de la entrada de Carla; Carla puede corregirla.*

- **Límite:** incluso el modelo final acierta poco en términos absolutos: F1 macro 0,172 y accuracy 0,179. La clase 1 (victoria local ajustada) apenas se recupera (recall 0,098) y la confusión más frecuente es 5 → 4 (288 partidos). Con ocho features de forma y goles, el techo está en los datos, no en el algoritmo.
- **Límite:** en la comparación de una temporada, Random Forest (0,180) y XGBoost (0,177) se separan 0,003, mucho menos que la desviación entre folds. Esa tabla no basta para elegir; la decisión se apoyó en las 9 temporadas y en el control de sobreajuste.
- **Aprendizaje:** la accuracy engaña con clases desbalanceadas. La referencia saca 0,443 prediciendo siempre la clase 5. Decidir con F1 macro y validar todos los modelos con el mismo `stratified_cv()` es lo que hace comparables las tablas.
- **Aprendizaje:** controlar el sobreajuste cuesta poco y vale mucho. Con los parámetros por defecto el gap era 0,505; la rejilla con `GAP_THRESHOLD` lo bajó a 0,0496 a cambio de 0,008 de F1 macro, y si ninguna combinación cumple, la búsqueda falla en vez de entregar un modelo sobreajustado.

## 9.3 Eva · App, base de datos, despliegue y MLOps

- **Límite:** el modelo está fijo desde el 16/11 y el feedback depende de la gente. Hoy hay muy pocas respuestas y nadie verifica la clase real, así que el acierto en tiempo real todavía no dice nada. Próximo paso: rellenar la clase real con los resultados oficiales de la misma fuente y reentrenar con el proceso que ya existe (export, drift, A/B testing y promoción con regla fija).
- **Límite:** la app vive en el plan gratuito de Render (se duerme tras 15 minutos) y el despliegue es manual. Suficiente para el proyecto; para un uso real haría falta un plan de pago y despliegue automático.
- **Aprendizaje:** un contrato entre la app y el modelo (`Predictor`) permitió desplegar desde el primer día con un modelo provisional y conectar el modelo final sin tocar la app.
- **Aprendizaje:** el contrato no basta. La app calculaba las features distinto que el entrenamiento, y lo descubrimos comparando con partidos reales, no con tests. Desde entonces una sola función y un test lo garantizan.
- **Aprendizaje:** medir antes de publicar. Con una temporada, el modelo optimizado no superaba al provisional; con nueve, el F1 macro se dobló (0,172 frente a 0,080). Y los tests deben ejecutarse con las mismas dependencias que producción: en el PR #77, quitar LightGBM del runtime habría roto la carga del modelo con el CI en verde.

## 9.4 Mariana · Red neuronal, MLOps y producto

*Redactada por Eva el 18/11 a partir de las secciones [1](01-problema.md), [5](05-red-neuronal.md) y [7a](07a-mlops-flujo-y-drift.md), a falta de la entrada de Mariana; Mariana puede corregirla.*

- **Límite:** la red neuronal se comparó con una sola temporada (359 partidos) y quedó por debajo de los árboles (F1 macro 0,129 frente a 0,180 del Random Forest). No se repitió con las 9 temporadas del modelo final. Próximo paso: repetir el comando de la sección 5.3 con el CSV de 9 temporadas.
- **Límite:** el ciclo de MLOps existe, pero es manual: drift con PSI, `promote` con una regla fija, commit del modelo y despliegue a mano. Para un uso real habría que automatizarlo.
- **Aprendizaje:** una accuracy más alta no es un modelo mejor. La red acierta más que los árboles (0,354 frente a 0,228) porque se pega a la clase 5 y casi no ve las clases 0 y 4. Solo con la misma validación y F1 macro se ve.
- **Aprendizaje:** el producto se define por lo que no promete: un tipo de resultado en 6 clases, no el marcador. Versionar el modelo y su ficha en git (la excepción de la #35) fue lo que permitió que el modelo llegara a producción.
