# poc_clean/ — versiones limpias para mostrarle al asesor

Esta carpeta tiene las versiones "de presentación" de cada PoC: mismo pipeline y mismos
resultados ya validados en `poc1/`, `poc2/`, etc., pero reorganizados en notebooks documentados,
pensados para correr por partes y mostrar avances al asesor — no para introducir nueva
metodología. Las decisiones metodológicas y el detalle técnico completo siguen viviendo en las
carpetas originales (`../poc1/`, `../poc2/`); ver [`../CLAUDE.md`](../CLAUDE.md) para el contexto
completo del proyecto.

## Contenido

- [`POC1/`](POC1/) — ML1 (Random Forest, con comparación contra Logistic Regression, XGBoost y SVM)
  sobre datos reales de LifeSnaps (n=71). Ver [`POC1/README.md`](POC1/README.md).
- [`POC1_1/`](POC1_1/) — POC 1.1 (validación solo con las 37 personas que tienen etiqueta real) y POC 1.2 (quitar
  grupos de variables). Notebook: [`POC1_1/POC1_1_Validacion.ipynb`](POC1_1/POC1_1_Validacion.ipynb). Hallazgos en
  [`POC1/POC1_FINDINGS.md`](POC1/POC1_FINDINGS.md).
- [`POC1_3/`](POC1_3/) — POC 1.3: en vez de una etiqueta por percentil, el modelo predice un puntaje continuo y el
  riesgo se obtiene con un corte fijo. Incluye la explicación de cómo se calcula el valor y un ejemplo de la salida de
  ML1. Notebook: [`POC1_3/POC1_3_Puntaje_continuo.ipynb`](POC1_3/POC1_3_Puntaje_continuo.ipynb).
- [`POC1_5/`](POC1_5/) — POC 1.5: laboratorio sintético con verdad conocida. Compara etiqueta por percentil, corte fijo y
  puntaje continuo cuando la población cambia (todos duermen mal, mixta, todos bien), y estima qué esperar con 50 personas
  según cuánto del puntaje refleje el reloj. No mide desempeño real. Notebook:
  [`POC1_5/POC1_5_Sintetico.ipynb`](POC1_5/POC1_5_Sintetico.ipynb).
- [`POC_FINAL/`](POC_FINAL/) — POC final: explicaciones SHAP agrupadas + regla de niveles Leve / Moderado / Alto +
  payload para el LLM. Notebook: [`POC_FINAL/POC_Final_SHAP.ipynb`](POC_FINAL/POC_Final_SHAP.ipynb).
- [`INFORME_POCs.md`](INFORME_POCs.md) — informe corto de todos los PoC (POC1, 1.3, 1.5, final), cortes de niveles y
  por qué el PSQI real sería mejor.
- [`POC_LLM/`](POC_LLM/) — PoC del LLM: recomendaciones a partir del nivel y los factores SHAP (C0 solo nivel / C1 con factores /
  C2 factores verbalizados por código), validador automático y respaldo. Notebook: [`POC_LLM/POC_LLM.ipynb`](POC_LLM/POC_LLM.ipynb).
- [`POC_GLOBEM/`](POC_GLOBEM/) — PoC con GLOBEM (Fitbit, 705 persona-años de universitarios, sin PSQI): estabilidad por persona,
  validez convergente con cuestionarios de salud mental, alerta del sedentarismo y variación del Random Forest con n = 37 a 635.
  Notebook: [`POC_GLOBEM/POC_GLOBEM.ipynb`](POC_GLOBEM/POC_GLOBEM.ipynb). Evidencia de apoyo, no es la prueba de riesgo de sueño.
- [`multiwearable/`](multiwearable/) — PoC multi-wearable: investigación de qué variables entrega cada marca de reloj
  Android (Fitbit, Samsung, Amazfit, Xiaomi) vía Health Connect / Google Health API
  ([`variables_por_plataforma.md`](multiwearable/variables_por_plataforma.md)) y un ensayo exploratorio
  ([`POC_Multiwearable.ipynb`](multiwearable/POC_Multiwearable.ipynb)): costo de usar solo las variables de cada reloj y
  prototipo de la capa de estandarización. Con datos reales de Xiaomi y el PSQI de MMASH:
  [`POC_Multiwearable_Datos_Reales.ipynb`](multiwearable/POC_Multiwearable_Datos_Reales.ipynb). Robustez del modelo generalizado con
  sesgos por marca tomados de la literatura y prueba de aproximar sedentarios:
  [`POC_Multiwearable_Robustez.ipynb`](multiwearable/POC_Multiwearable_Robustez.ipynb).
