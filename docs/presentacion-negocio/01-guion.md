# Presentación de negocio · guion

**Presenta:** Mariana · **Duración:** ~6 minutos · **7 diapositivas** · Canva (enlace cuando esté el archivo)

Cifras de acierto: las pone Cala en la sección 4; hasta entonces la diapositiva 5 lleva el hueco «F1 macro = …».

---

## 1. La kiniela no es un 1X2

**Se ve:** «6 tipos de resultado» y las seis clases en una fila.

**Se dice:** «Quien rellena una quiniela no apuesta solo a local, empate o visitante. Un 4-0 no se juega igual que un 1-0. Por eso clasificamos el partido en seis tipos: victoria clara o ajustada a cada lado, empate, o festival de goles.»

## 2. Para quién

**Se ve:** una persona con el móvil, no un banquillo.

**Se dice:** «No es una herramienta de club. Es para quien rellena la kiniela: elige dos equipos y ve qué tipo de partido esperar.»

## 3. El producto

**Se ve:** captura de https://kiniela-predictor.onrender.com con clase y seis probabilidades.

**Se dice:** «Hoy ya se puede usar. La app te da la clase más probable y las seis probabilidades. Después puedes decir si acertó. Eso no es un adorno: es dato para el siguiente modelo.»

## 4. Lo que dicen los datos

**Se ve:** «La clase 5 (4+ goles) es muy frecuente» y «las claras son raras».

**Se dice:** «En Premier, muchos partidos se van a cuatro goles o más. Si el modelo solo persiguiera acierto global, aprendería a cantar “muchos goles” y ya. Por eso miramos F1 por clase, no solo el porcentaje global.»

*(Anna puede sustituir esto por un número del EDA cuando esté la sección 2.)*

## 5. Qué tan bien predice

**Se ve:** una métrica grande (F1 macro del candidato de Cala) y la clase que peor sale.

**Se dice:** «La métrica que nos importa pondera las seis clases igual. El modelo de prueba de la web, hoy, es el reparto histórico; el modelo entrenado se enchufa sin cambiar la app cuando Cala y el contrato coincidan.»

**Hueco:** `F1 macro = ___` · clase más débil = `___`.

## 6. Cómo mejora con el uso

**Se ve:** App → feedback → export → reentrenar → promocionar.

**Se dice:** «Cada acierto o error con la clase real se guarda. Un comando saca esos partidos, se unen al histórico y se vuelve a entrenar. Si el modelo nuevo gana, sustituye al de la app. Si los datos nuevos se parecen poco a los de entrenamiento, el PSI nos avisa antes de mezclarlos.»

## 7. Límites y siguiente paso

**Se ve:** tres límites y un siguiente paso.

**Se dice:** «No prometemos el marcador. El plan gratuito duerme la app. Hasta promocionar el modelo final, avisamos que es un modelo de prueba. El siguiente paso es conectar el candidato de Cala a la app y seguir recogiendo feedback real.»
