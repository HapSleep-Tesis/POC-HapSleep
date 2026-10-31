# Prompt para NotebookLM — fuentes del benchmark de LLM

Pegar en el cuaderno que tiene las fuentes de la tesis. **No se inventó ninguna cita en el informe**: donde falta la fuente, el Word tiene la marca amarilla `[FUENTE: …]`. Con lo que responda NotebookLM se completan esas marcas.

---

Responde **solo con lo que dicen las fuentes cargadas**. Para cada afirmación dame la cita en **APA 7** (autores, año, título, revista, DOI o URL). Si ninguna fuente respalda lo que te pido, escribe exactamente "SIN FUENTE" y no completes con conocimiento propio. No parafrasees de memoria referencias que no estén cargadas.

Contexto: HapSleep es una app que estima el riesgo de mala calidad de sueño de estudiantes universitarios con un random forest y SHAP; un LLM recibe **solo el nivel de riesgo y los factores principales** (sin datos que identifiquen al estudiante) y redacta una recomendación breve en español. El nivel lo decide una regla fija, nunca el LLM. Estoy haciendo un benchmark de LLM candidatos: GPT en Azure OpenAI, Gemma 3 (modelo abierto, 4B) y DeepSeek-R1-Distill-Qwen-7B (modelo abierto de razonamiento).

Necesito, en este orden:

**A. Fuentes de los candidatos.** Una fuente citable (informe técnico, artículo o documentación oficial) para cada uno: (1) GPT servido por Azure OpenAI; (2) Gemma 3; (3) DeepSeek-R1 y sus modelos destilados. Si están cargadas como documentos, dame la cita; si no, "SIN FUENTE".

**B. Fuentes de los criterios.** Para cada criterio, una o dos fuentes que justifiquen medirlo en un LLM que da recomendaciones de salud o bienestar:
1. **Seguridad de la respuesta**: riesgos de que un LLM dé diagnósticos, consejos médicos inseguros o afirme causas en salud/bienestar.
2. **Coherencia con los factores enviados** (no inventar datos): alucinaciones de LLM en salud y cómo reducirlas dando información estructurada o explicaciones (SHAP/XAI) en el prompt.
3. **Cumplimiento de la validación automática**: validadores, guardrails o filtros de salida para respuestas de LLM (por ejemplo, reglas sobre longitud, idioma o contenido) y sus límites.
4. **Tiempo de respuesta**: latencia de LLM como criterio de selección, sobre todo en procesos por lotes.
5. **Privacidad y control de los datos**: envío de datos de salud a un LLM en la nube frente a ejecutarlo en infraestructura propia; residencia de datos.

**C. Fuentes para el análisis.** Si existen en las fuentes:
- Comparaciones entre LLM pequeños abiertos y LLM comerciales para generar recomendaciones de salud o bienestar en español.
- Evaluación de recomendaciones de LLM con **rúbricas de expertos** (pertinencia, claridad, aplicabilidad, tono).
- Estudios de LLM que redactan a partir de **factores SHAP** o explicaciones de un modelo de ML.

**Formato de salida.** Tres tablas en Markdown:
1. `Propuesta | Fuente (APA 7) | ¿Está en mis fuentes? (sí / SIN FUENTE)`
2. `Criterio | Fuente(s) (APA 7) | Qué dice la fuente sobre este criterio, en una frase`
3. `Tema del punto C | Fuente (APA 7) | Hallazgo en una frase`

Al final, lista aparte los DOI o URL que hay que **verificar contra el PDF original**.
