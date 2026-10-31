# HapSleep: resumen de la prueba de concepto (para redactar el paper)

Contexto para quien redacte: tesis de ingeniería de software. El producto es una app que, con datos de smartwatch, estima el riesgo de mala calidad de sueño de estudiantes universitarios de Lima y entrega una recomendación redactada por un LLM. Todo lo de abajo viene de pruebas hechas con datasets públicos y **una etiqueta sustituta, no el PSQI** (todavía no hay PSQI de estudiantes). Es la versión 1 del paper; la versión 2 repetirá el análisis con PSQI. Los resultados son de diseño, **no el desempeño final**.

## Flujo del sistema
Smartwatch → resumen por persona → Random Forest (estima un índice de riesgo continuo) → SHAP (explica en 5 grupos de factores) → regla fija en código (nivel Leve / Moderado / Alto) → LLM (redacta la recomendación) → validador (si falla, plantilla de respaldo) → app.
El **nivel lo decide el código, nunca el LLM**. El LLM solo redacta.

## Datos
- **LifeSnaps** (Fitbit Sense): 71 personas, 7,410 filas persona-día. Cita: Yfantidou et al. (2022), *Scientific Data*, 9, 663, https://doi.org/10.1038/s41597-022-01764-x
- **Etiqueta sustituta:** "puntaje de sueño de Fitbit" (columna `sleep_points_percentage`). Es un derivado del Stress Score de Fitbit, no el Sleep Score de 1 a 100. Existe solo para **37 de las 71** personas.
- **Variables (11):** frecuencia cardíaca en reposo, pulso durante el sueño, HRV, saturación de oxígeno, frecuencia respiratoria, latencia, minutos dormido, minutos despierto, eficiencia del sueño, pasos, minutos sedentarios. Cada una se resume por persona con media y desviación estándar entre días: **22 números por estudiante**. La latencia no es utilizable (99.4 % de ceros).
- **GLOBEM** (apoyo): 705 persona-años de universitarios, 4 cohortes de primavera (2018 a 2021), Fitbit (solo sueño y pasos) + cuestionarios de salud mental. **No tiene PSQI ni pulso, HRV, SpO2 ni respiración.** PhysioNet, versión 1.1, licencia credencializada (se cita, no se redistribuye).

## Método
- Se agrega por persona porque el riesgo es un rasgo estable y una noche puntual es casi impredecible.
- Comparación de modelos: Random Forest, regresión logística, XGBoost, SVM. Riesgo alto = 25 % con peor puntaje. Validación cruzada de 5 particiones repetida 20 veces; F1, ROC-AUC, PR-AUC contra baseline (nunca accuracy sola).
- Deep Learning se descartó: la literatura de la tesis solo lo usa sobre señales crudas, no sobre datos agregados con pocas personas.
- Explicaciones: Random Forest estima un **índice continuo** (más alto es peor, como el PSQI); TreeSHAP agrupado en 5 grupos (duración y eficiencia, regularidad, frecuencia cardíaca y HRV, respiración y oxígeno, actividad y sedentarismo) porque las variables están correlacionadas. Cada persona se evalúa con un modelo entrenado con las otras 36.
- Se usa índice continuo + corte fijo y no percentil, porque el percentil siempre marca ~25-30 % de riesgo alto sin importar cómo duerma la población (se vio en datos simulados).

## Resultados
**1. Elección del modelo (71 personas)**

| Modelo | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|
| Random Forest | 0.478 ± 0.077 | 0.728 ± 0.033 | 0.481 ± 0.046 |
| Regresión logística | 0.462 ± 0.078 | 0.669 ± 0.051 | 0.428 ± 0.059 |
| XGBoost | 0.414 ± 0.077 | 0.755 ± 0.037 | 0.493 ± 0.049 |
| SVM | 0.088 ± 0.092 | 0.668 ± 0.039 | 0.397 ± 0.044 |

Azar: ROC-AUC 0.5, PR-AUC 0.25. **Ningún modelo gana en todo; Random Forest no se eligió por ganar.** XGBoost tiene mejor ROC-AUC, pero la diferencia (0.027) es menor que una desviación estándar (0.033). Se eligió Random Forest porque no pierde desempeño relevante y porque TreeSHAP da explicaciones exactas por persona, que es lo que necesita el LLM. El ROC-AUC es moderado por: pocos datos, etiqueta ruidosa (34 personas rellenadas con la mediana en la primera prueba) y porque el reloj solo mide parte del PSQI (duración, eficiencia, latencia; no calidad subjetiva, medicación ni somnolencia). El 0.73 es una cota conservadora.

**2. Índice continuo y explicaciones (37 personas)**
- Spearman 0.70; error medio 2.1 puntos en escala 0-21 contra 3.3 de predecir siempre el promedio.
- SHAP suma exacto a la estimación; neutralizar el grupo señalado baja el índice 0.096 (contra 0.001 con un grupo cualquiera); el grupo principal es el mismo en 20 de 20 repeticiones; coincide con la importancia clásica (Spearman 0.96). Los demás grupos cambian de orden: solo el principal es estable.
- **Niveles:** Leve ≤ 5, Moderado 6 a 10, Alto > 10 (escala PSQI). **Solo el corte de 5 está validado** (Buysse et al., 1989, *Psychiatry Research*, 28(2), 193-213; ">5" = mal dormidor, sensibilidad 89.6 %, especificidad 86.5 %). El 10 es una convención clínica de derivación, sin validación. Los cortes finales los define el equipo.
- El nivel coincidió con el del puntaje de referencia en 62 % (49 % si siempre se respondiera el más frecuente). El modelo se contrae al centro: 1 Leve, 24 Moderado, 12 Alto (referencia: 8, 18, 11).

**3. LLM (37 casos; Gemma 3 4B y DeepSeek-R1-Distill 7B, locales en CPU)**
Tres condiciones: C0 solo el nivel; C1 nivel + factores con valores; C2 factores ya redactados por código con su sentido (por encima/por debajo de lo típico, sube/baja el riesgo).
- Sin factores (C0) el LLM inventa (estrés, pantallas) en casi 9 de 10 textos.
- Con factores (C1): 97 % menciona el factor principal, pero **46 % contradice algún valor**. Con C2 baja a 22 % (McNemar p = 0.02).
- Gemma: 100 % de textos seguros (sin diagnóstico, medicación ni causa afirmada), 59 % pasa el validador con C1, 14 s por texto. DeepSeek (8 casos): 7 de 8 seguros, 58 s por texto. La plantilla de respaldo pasa el validador en 37 de 37.
- **GPT en Azure OpenAI (propuesto en el diseño) no se ejecutó.** No hubo evaluación experta de utilidad de las recomendaciones.
- El validador es heurístico (listas de palabras) y se ajustó después de leer los primeros textos.

**4. GLOBEM (apoyo)**
- Estabilidad: autocorrelación noche a noche entre −0.04 y 0.07, pero el resumen por persona se repite entre noches pares e impares (0.84 a 0.98).
- La **regularidad** (variación de la duración del sueño y del horario de acostarse) se relaciona +0.18 a +0.30 con cuestionarios de salud mental en las 4 cohortes. CES-D y BDI-II incluyen ítems de sueño, así que parte es mecánica; con PSS-10 es menor. Eficiencia, minutos despierto, pasos y sedentarios no resisten la corrección por 28 pruebas.
- Minutos sedentarios + activos = 1440 exacto y correlación −0.92 con pasos: no aportan información propia.
- **Pocas personas:** con estrés (PSS-10) como etiqueta sustituta (otro constructo, solo para medir variabilidad), a n = 50 Random Forest da Spearman mediano 0.01 (−0.18 a 0.36 en 90 % de corridas), igual que con etiquetas mezcladas; con n = 635 da 0.18. Una sola variable elegida de antemano (variación de la duración del sueño) rinde igual o mejor (0.21 a n = 50). Entrenando en 3 años y probando en el 4.º, el modelo queda peor que el promedio en 2020 (pandemia).

## Otras pruebas (solo si hace falta)
- Con solo las variables comunes a varios relojes (sin minutos sedentarios), el Spearman bajó de 0.70 a 0.36-0.43. Los sesgos de marca conocidos casi no degradaron el modelo, pero solo porque el modelo casi no usa variables de sueño con esta etiqueta. Datos reales de otra marca: solo 4 usuarios Xiaomi.

## Qué NO afirmar
- Que el sedentarismo es el factor principal: su media correlaciona 0.88 con el tiempo que el reloj estuvo puesto, y en GLOBEM no se relaciona con nada.
- Que el modelo predice calidad de sueño real o que 0.73 es el desempeño final.
- Que el corte de 10 es un estándar.
- Que Random Forest es el mejor modelo en desempeño.
- Que SHAP muestra causas (solo factores asociados).
- Que GPT funcionó o que las recomendaciones del LLM son útiles (no se evaluó).
- Que GLOBEM valida el riesgo de sueño (no tiene PSQI).

## Citas: qué está y qué no
- **Verificadas en las páginas del proyecto:** Yfantidou et al. (2022); GLOBEM (PhysioNet 1.1); Buysse et al. (1989) como referencia estándar, aunque **sin contrastar con el artículo original**.
- **Sin verificar o sin fuente (pedir al otro chat que busque en sus fuentes):** respaldo para descartar Deep Learning (Kim et al., 2025; Aziz et al., 2025, vienen de una búsqueda asistida), umbrales de Cohen (1988) para interpretar correlaciones, sesgos por marca de reloj contra polisomnografía (Schyvens 2025, JMIR 2023, J Sleep Med 2023), y riesgos de consejos de salud de un LLM. No inventar citas: si falta la fuente, marcarla como pendiente.
