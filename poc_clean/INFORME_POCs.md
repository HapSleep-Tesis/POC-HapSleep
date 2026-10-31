# HapSleep — Informe de los PoC de ML1

Resumen de lo hecho hasta ahora, en orden. Cada PoC tiene su notebook ejecutado en `poc_clean/`; los números de abajo salen de ahí.

**Qué es ML1:** el modelo que estima el riesgo de mala calidad de sueño de un estudiante a partir de datos de smartwatch. Su salida (nivel + factores) la recibe un LLM que redacta la recomendación en la app.

**Aviso general:** todo se hizo con un **proxy** de la etiqueta (LifeSnaps no tiene PSQI). Estos PoC ensayan el **diseño**; no son el desempeño final.

---

## POC 1 — Modelo de ML con datos reales

- **Datos:** LifeSnaps (Fitbit Sense), 71 personas, 7,410 filas persona-día, 11 variables de reloj (sueño, pulso en reposo, HRV, SpO2, respiración, pasos, minutos sedentarios).
- **Cómo se armó:** cada variable se resume por persona (media y desviación estándar entre sus días → 22 números). El riesgo es un rasgo estable de la persona, no de una noche.
- **Etiqueta (proxy):** "riesgo alto" = 25 % peor del `sleep_points_percentage` (el "puntaje de sueño de Fitbit").
- **Evaluación:** 5-Fold repetido 20 veces, media ± desviación. Se reporta F1, ROC-AUC y PR-AUC contra un baseline; nunca accuracy sola.

| Modelo | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|
| **Random Forest (elegido)** | 0.478 ± 0.077 | 0.728 ± 0.033 | 0.481 ± 0.046 |
| Regresión logística | 0.462 | 0.669 | 0.428 |
| XGBoost | 0.414 | 0.755 | 0.493 |
| SVM | 0.088 | 0.668 | 0.397 |

(Con 25 % de riesgo alto, el azar da PR-AUC = 0.25 y ROC-AUC = 0.5.)

- **Por qué Random Forest:** no pierde desempeño relevante frente a los otros y es interpretable. Deep Learning se descartó con respaldo de la literatura de la tesis (los usos de DL en el área son sobre señales crudas, otra tarea).
- **Advertencia sobre la etiqueta:** ese puntaje existe solo para 37 de las 71 personas; a las otras 34 se les rellenó con la mediana y quedaron como "riesgo bajo". Además es un componente del Stress Score de Fitbit, no el Sleep Score de 1–100. Por eso 0.73 es una cota conservadora y no un techo.

## POC 1.3 — Puntaje continuo en vez de percentil

- **Problema del percentil:** siempre marca ~25–30 % como riesgo alto, sin importar cómo duerma la población. Si casi todos duermen mal, no sirve.
- **Qué se hizo:** con las 37 personas con puntaje real, el modelo predice un **índice continuo** (1 − puntaje; más alto = peor, como el PSQI) y el riesgo se decide después con un **corte fijo**.
- **Resultado (Random Forest):** Spearman 0.70, error medio 0.108 frente a 0.165 del baseline (35 % menos), R² 0.45. Con cortes que dejan entre 22 % y 78 % de personas en riesgo alto, ROC-AUC 0.79–0.93.
- **Salida propuesta:** índice estimado + rango de incertidumbre + zona gris + factores + calidad de datos.

## POC 1.5 — Laboratorio con datos sintéticos

- **Qué es:** poblaciones simuladas donde **sabemos** el puntaje verdadero de cada persona. Sirve para comparar diseños y planificar; **no mide desempeño real** y depende de los supuestos del simulador.
- **Lo que mostró:**
  1. El **percentil marca ~30 % en cualquier población**; donde casi todos duermen mal (77 % en riesgo real) detecta apenas 37 % de los casos. El **corte fijo** sigue a la realidad.
  2. El puntaje continuo con corte **se contrae hacia el promedio** cuando el reloj refleja poco del puntaje.
  3. **El F1 solo engaña** con prevalencia alta: se parece al de un modelo que siempre dice "alto". Hay que mirar ROC-AUC contra el baseline.
  4. **Con 50 personas** el ROC-AUC varía ~±0.1 solo por quiénes te toquen. Lo que más pesa es cuánto del puntaje refleja el reloj: ROC-AUC 0.75 si lo refleja bastante (r = 0.7) y 0.63 si poco (r = 0.5).

## POC final — SHAP + niveles Leve / Moderado / Alto

Notebook: [`POC_FINAL/POC_Final_SHAP.ipynb`](POC_FINAL/POC_Final_SHAP.ipynb). Ejemplo de salida para el LLM: [`POC_FINAL/payload_examples.json`](POC_FINAL/payload_examples.json).

**Flujo (Reloj → ML → SHAP → nivel → LLM → App):**
1. El Random Forest estima el índice de cada persona sin haberla visto (se entrena con las otras 36).
2. **TreeSHAP** descompone esa estimación: cuánto suma o resta cada variable. Se **agrupan** en 5 grupos (duración/eficiencia, regularidad, pulso y HRV, respiración/oxígeno, actividad) porque el paper advierte que SHAP se distorsiona con variables correlacionadas.
3. Una **regla fija** convierte el índice en Leve / Moderado / Alto. **La decide el código, no el LLM**, para que la misma persona no reciba niveles distintos según el día.
4. El LLM recibe el nivel ya decidido + los factores (los que suben el riesgo, el que más lo baja, valor real vs. típico) y solo redacta.

**Resultados (37 personas, proxy):**

| Prueba | Resultado |
|---|---|
| SHAP suma exacto a la estimación | Sí (error ~1e-15) |
| Neutralizar el grupo señalado por SHAP | El índice baja +0.096; con un grupo cualquiera, −0.001. En 94 % de las personas baja más |
| Estabilidad (20 repeticiones al 80 %) | El grupo principal es el mismo las 20 veces (*Actividad y sedentarismo*); el orden del resto cambia (acuerdo 0.69) |
| SHAP vs. importancia clásica (Gini) | Coinciden en las variables principales (Spearman 0.96) |
| Nivel estimado vs. nivel del proxy | Igual en 62 % (49 % si siempre dijera el más frecuente); nunca más de un nivel de diferencia |

**Límites:**
- El modelo **se contrae hacia el centro**: 24 de 37 quedan en Moderado y solo 1 en Leve (el proxy dice 8). Ya lo anticipaba POC 1.5.
- Solo el factor principal es estable; los demás deben presentarse como secundarios.
- El factor dominante (minutos sedentarios) probablemente **no existe en Health Connect**, y no se descarta que su peso venga en parte de cómo se construye el proxy. Se revisa con el PSQI.
- **Alerta posterior (multi-wearable, robustez):** el promedio de minutos sedentarios correlaciona +0.88 con los minutos totales que el reloj registró, y el riesgo del proxy correlaciona +0.68 con esos minutos; al quitar el efecto de uno sobre el otro quedan +0.29 y +0.20. La señal principal no se separa de cuán completos están los datos, así que no debe presentarse "sedentarismo" como hallazgo ni como factor principal hasta repetirlo con el PSQI.
- SHAP explica al **modelo**, no la causa real: el LLM debe hablar de factores "asociados", no de causas.

### Cómo se eligieron los cortes de los niveles

- Se buscó si el PSQI (0–21, más alto = peor) trae niveles oficiales. El estudio original define **solo dos grupos**: buen dormidor **≤ 5** y mal dormidor **> 5** (sensibilidad 89.6 %, especificidad 86.5 %). **No hay una división validada en leve / moderado / severo.** El corte **> 10** se usa como umbral de derivación, pero es convención.
- **Propuesta: Leve ≤ 5 · Moderado 6–10 · Alto > 10.** El primer corte tiene validación; el segundo es convención, y así hay que decirlo en la tesis. Los define el equipo; esto es una propuesta con fuente.
- Alternativa descartada: tres tercios iguales de la escala (0–7 / 8–14 / 15–21). Es simple, pero ignora el único corte validado.
- Como el proxy no es PSQI, en el ensayo el índice 0–1 se multiplicó por 21. Con el PSQI real los cortes se aplican directo.
- Pendiente: el proyecto venía usando "PSQI ≥ 5 = mala calidad" y Buysse define "> 5". Hay que unificar.
- Fuentes consultadas (sin verificar contra los PDFs originales): [PSQI en Pitt](https://www.sleep.pitt.edu/psqi), [Buysse 1989](https://pubmed.ncbi.nlm.nih.gov/2748771/), [revisión breve del PSQI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11973415/).

---

## Con el PSQI real sería mejor

| Hoy (proxy) | Con PSQI |
|---|---|
| Etiqueta derivada del Stress Score de Fitbit, solo 37 de 71 personas (34 rellenadas) | Todas las personas tienen etiqueta |
| Viene del mismo reloj: riesgo de circularidad y fugas | Fuente independiente del reloj |
| Los cortes son del proxy, sin estándar | Cortes con respaldo (≤ 5 / > 5) y comparables con la literatura |
| "Predice un puntaje de Fitbit" | "Estima el PSQI de estudiantes de Lima" |

**Qué cambia al pasar al PSQI:** solo la función de etiqueta y los cortes se aplican directo; el pipeline, SHAP y los niveles quedan igual. **Ojo:** el PSQI es autorreporte (limitación reconocida en el paper), el reloj mide solo parte de sus componentes (duración, eficiencia, latencia; no calidad subjetiva, medicación ni somnolencia), y se necesita recolectar n ≥ 50. Los datos de reloj deben ser del mismo periodo que evalúa el cuestionario.

## Ajustes sugeridos al paper (variables)

| Paper dice | En los datos | Propuesta |
|---|---|---|
| Tiempo total de sueño, eficiencia, FC en reposo | Disponibles (69–71 personas) | Se quedan |
| Regularidad noche a noche | Variación de la duración | Se queda (de duración, no de horario) |
| **Latencia de sueño** | 99.4 % ceros (Fitbit pone 0 por defecto) | **Sacarla** |
| HRV | Solo 43 de 71 personas | Se queda, con la limitación |
| Horario de sueño | No está en las variables | Quitarlo o dejarlo como trabajo futuro |
| — | Minutos despierto, pasos, sedentarismo, SpO2, respiración | Agregarlos a la lista de variables (los dos primeros salen entre los factores principales) |
| "Evita alucinaciones" (resumen del C3) | — | Decir "reduce" (el propio paper dice que los guardrails no las eliminan) |

## Qué sigue

1. **PoC del LLM:** recomendaciones a partir de `payload_examples.json`, comparando con y sin factores SHAP.
2. **Recolección del PSQI** (n ≥ 50) para reemplazar el proxy y volver a correr todo.
3. PoC multi-wearable (investigación en `multiwearable/variables_por_plataforma.md`, sin correr).
