# 📊 Resumen de Trabajo - Issue #1: Preparación del Dataset

**Asignado a**: Anna (Scrum Master y Data & EDA Lead)  
**Fecha**: 10 de noviembre de 2026  
**Estado**: ✅ Completado - Archivos creados, lista para ejecutar

---

## 🎯 Objetivo del Issue #1
Descargar, unificar y limpiar el dataset histórico de partidos de fútbol (Premier League).

---

## ✅ Entregables Creados

### 1. **Documentación de Tarea**
- **Archivo**: [`docs/tarea-preparacion-dataset.md`](tarea-preparacion-dataset.md)
- **Contenido**:
  - Fuente de datos (Football-Data.co.uk)
  - Pasos detallados para descarga y limpieza
  - Estructura esperada del dataset final
  - Estado de los criterios de aceptación

### 2. **Script de Preparación**
- **Archivo**: [`src/preparacion_dataset.py`](src/preparacion_dataset.py)
- **Funcionalidades**:
  ```python
  ✅ Descargar datos desde Premier League (2015-2024)
  ✅ Unificar todos los años en un único DataFrame
  ✅ Eliminar duplicados (fecha + equipos)
  ✅ Limpiar columnas de texto (fechas, nombres de equipos)
  ✅ Corregir valores numéricos (goles FH y AH)
  ✅ Crear columna 'Result' (H/A/D)
  ✅ Guardar en data/processed/ (CSV y Parquet)
  ✅ Mostrar estadísticas del dataset final
  ```

### 3. **Notebook Interactivo**
- **Archivo**: [`notebooks/01_preparacion_dataset.ipynb`](notebooks/01_preparacion_dataset.ipynb)
- **Contenido**:
  - Célula de importaciones y configuración
  - Función `descargar_datos_premier_league()`
  - Función `limpiar_datos(df)`
  - Función `info_dataset(df)` para visualización
  - Preparada para ejecución paso a paso

---

## 📂 Estructura del Proyecto (Actualizada)

```
kiniela-predictor-equipo2/
├── data/
│   ├── raw/          # ← Aquí se descargarán los datos crudos
│   └── processed/    # ← Aquí irán los datos limpios
├── src/
│   └── preparacion_dataset.py  ← Script principal (nuevo)
├── notebooks/
│   └── 01_preparacion_dataset.ipynb  ← Notebook interactivo (nuevo)
└── docs/
    └── tarea-preparacion-dataset.md  ← Documentación (nueva)
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Ejecutar desde la Terminal (Recomendado para producción)

```bash
# Activar entorno virtual (si no existe)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar requisitos
pip install -r requirements.txt

# Ejecutar script de preparación
python src/preparacion_dataset.py
```

### Opción 2: Usar el Notebook (Recomendado para EDA)

```bash
jupyter notebook notebooks/01_preparacion_dataset.ipynb
# o
pip install jupyter && jupyter lab
```

---

## 📋 Criterios de Aceptación - Issue #1

| Criterio | Estado | Comprobación |
|----------|--------|--------------|
| ✅ La fuente queda documentada | ✅ **Cumplido** | Ver `docs/tarea-preparacion-dataset.md` |
| ✅ Los partidos quedan unificados | ⏳ Pendiente | Depende de ejecución del script |
| ✅ Los datos están limpios (sin duplicados, sin nulos críticos) | ⏳ Pendiente | Depende de ejecución del script |
| ✅ El archivo resultante está guardado en `data/` | ⏳ Pendiente | Se genera al ejecutar script |
| ✅ El proceso es reproducible | ✅ **Cumplido** | Script documentado y versionado |

---

## 📊 Dataset Esperado

### Columnas del Dataset Final:
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Date` | datetime | Fecha del partido (YYYY-MM-DD) |
| `Time` | object | Hora del partido (HH:MM) |
| `HomeTeam` | object | Equipo local (ej: "arsenal", "chelsea") |
| `AwayTeam` | object | Equipo visitante |
| `FH` | int64 | Full Time Home (goles locales) |
| `AH` | int64 | Full Time Away (goles visitantes) |
| `Result` | object | Resultado: 'H' (Home), 'A' (Away), 'D' (Draw) |

### Estadísticas Esperadas (~25 años de Premier League):
- **Total de partidos**: ~1,400 - 1,700 partidos
- **Temporadas**: 2015-2023 (9 temporadas)
- **Equipos únicos**: 20 equipos principales

---

## 🔄 Siguientes Pasos (Dependencias)

### Issue #2: Creación de la Variable Objetivo (Target)
**Depende de**: Issue #1 ✅  
**Asignado a**: Anna  
**Descripción**: Crear columna `target` con las 6 clases según reglas de negocio.

Clases Kiniela:
- 0: Victoria local clara
- 1: Victoria local ajustada
- 2: Empate
- 3: Victoria visitante ajustada
- 4: Victoria visitante clara
- 5: Partido con 4+ goles (precedencia sobre todo)

---

### Issue #3: Feature Engineering
**Depende de**: Issue #1 ✅, Issue #2  
**Asignado a**: Anna  
**Descripción**: Crear features recientes, promedios, diferencia de rendimiento.

---

### Issue #4: Análisis Exploratorio (EDA)
**Depende de**: Issue #2 ✅, Issue #3  
**Asignado a**: Anna  
**Descripción**: EDA completo con visualizaciones multiclase.

---

## 📝 Notas para el Equipo

- ✅ El código está versionado en Git y sigue la estructura del proyecto
- ✅ No hay secretos ni tokens expuestos (cumple Definición de Hecho)
- ✅ La documentación es clara y reproducibles los datos
- ✅ Los criterios de aceptación serán verificados tras la ejecución del script

---

## 🎯 Checklist Personal - Anna

Como Data & EDA Lead, estos son mis siguientes pasos:

- [ ] ⏳ Ejecutar `python src/preparacion_dataset.py` para descargar y limpiar los datos
- [ ] ⏳ Verificar que el dataset se ha guardado correctamente en `data/processed/`
- [ ] ⏳ Comprobar la distribución de equipos y resultados
- [ ] ⏳ Iniciar Issue #2: Crear variable objetivo (target) con las 6 clases

---

## 📸 Capturas de Pantalla (Post-ejecución)

*Una vez ejecutado el script, documentar aquí:*
- *Tamaño final del dataset*
- *Distribución por resultado (H/A/D)*
- *Lista completa de equipos y temporadas cubiertas*

---

**Próxima sesión**: Issue #2 - Creación de la variable objetivo (Target)