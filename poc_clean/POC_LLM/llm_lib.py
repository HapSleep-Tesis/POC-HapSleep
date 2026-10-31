"""Piezas del PoC del LLM de HapSleep: prompt, adaptadores de modelo, validador y plantilla de respaldo.

Sigue el diseño del Objetivo 2: el LLM recibe SOLO el nivel (ya decidido por una regla en código) y los factores
principales, sin datos que identifiquen al estudiante, y redacta una recomendación breve en español. El sistema la
valida antes de mostrarla; si falla, usa una recomendación de respaldo.

Todo lo de aquí es propuesta del PoC (longitud máxima, listas de palabras, plantillas): no viene de una norma.
"""
import os
import re
import time

PROMPT_VERSION = "v1"
MAX_PALABRAS = 80

SYSTEM_PROMPT = """Eres el asistente de HapSleep, una app que orienta a estudiantes universitarios sobre su sueño.
Recibirás un JSON con el nivel de riesgo de mala calidad de sueño, que YA fue calculado por otro modelo, y, si existen, los factores asociados a ese resultado. Escribe una recomendación breve para el estudiante.

Reglas:
1. Escribe en español, con tono cercano, hablándole de "tú".
2. Máximo 80 palabras, en un solo párrafo de 2 o 3 frases.
3. No cambies ni cuestiones el nivel de riesgo que recibes.
4. No diagnostiques, no nombres enfermedades ni trastornos y no recomiendes medicamentos ni suplementos.
5. No afirmes causas: los factores están "asociados" al resultado. Usa expresiones como "se asocia", "podría" o "suele ayudar".
6. Menciona solo los factores que aparecen en el JSON. No inventes datos ni otros factores.
7. Termina con una acción concreta y pequeña que pueda hacer hoy.
8. Si el nivel es Alto, sugiere conversar con bienestar universitario o un profesional de salud, sin alarmar."""

# ---- etiquetas legibles de las variables (lo que el LLM ve en lugar de nombres técnicos) ----
VARIABLE_LABELS = {
    "minutesAsleep_mean": "minutos de sueño por noche (promedio)",
    "minutesAwake_mean": "minutos despierto durante la noche (promedio)",
    "sleep_efficiency_mean": "eficiencia del sueño (promedio, %)",
    "minutesToFallAsleep_mean": "minutos que tarda en dormirse (promedio)",
    "sleep_duration_inconsistency": "variación de la duración del sueño entre noches (minutos)",
    "minutesAwake_std": "variación de los minutos despierto entre noches",
    "sleep_efficiency_std": "variación de la eficiencia del sueño entre noches",
    "minutesToFallAsleep_std": "variación de los minutos que tarda en dormirse",
    "resting_hr_mean": "frecuencia cardíaca en reposo (promedio, lpm)",
    "resting_hr_std": "variación de la frecuencia cardíaca en reposo",
    "nremhr_mean": "frecuencia cardíaca durante el sueño (promedio, lpm)",
    "nremhr_std": "variación de la frecuencia cardíaca durante el sueño",
    "rmssd_mean": "variabilidad de la frecuencia cardíaca, HRV (promedio, ms)",
    "rmssd_std": "variación de la variabilidad de la frecuencia cardíaca",
    "full_sleep_breathing_rate_mean": "frecuencia respiratoria durante el sueño (promedio)",
    "full_sleep_breathing_rate_std": "variación de la frecuencia respiratoria durante el sueño",
    "spo2_mean": "saturación de oxígeno durante el sueño (promedio, %)",
    "spo2_std": "variación de la saturación de oxígeno",
    "steps_mean": "pasos por día (promedio)",
    "steps_std": "variación de los pasos entre días",
    "sedentary_minutes_mean": "minutos sedentarios por día (promedio)",
    "sedentary_minutes_std": "variación de los minutos sedentarios entre días",
}

# palabras que delatan que un texto habla de cada grupo de factores (heurística del PoC)
GROUP_PATTERNS = {
    "Duración y eficiencia del sueño": r"duraci[oó]n|horas? de sue[ñn]o|eficiencia|tiempo (total )?(de sue[ñn]o|dormid)|dormir (m[aá]s|menos)|minutos de sue[ñn]o",
    "Regularidad del sueño (variación entre noches)": r"regular|irregular|horario|constan|variaci[oó]n|noche a noche|despert|acostar",
    "Frecuencia cardíaca y HRV": r"frecuencia card[ií]aca|pulso|latidos|\bhrv\b|variabilidad card",
    "Respiración y oxígeno": r"respiraci[oó]n|respirar|ox[ií]geno|spo2|saturaci[oó]n",
    "Actividad y sedentarismo": r"sedentar|sentad|actividad f[ií]sica|movimiento|pasos|camin|ejercicio|\bactiv[oa]s?\b|actividad",
}

# factores que NUNCA se envían al LLM (si aparecen, el modelo los inventó)
OTROS = r"estr[eé]s|cafe[ií]na|alcohol|ruido|luz azul|ansiedad"
# Ajuste posterior a leer los primeros resultados: lectura de valores. Palabras que dicen "más que lo típico" o "menos que lo típico"
ALTO = r"elevad|\balt[oa]s?\b|much[oa]s?\b|bastante|excesiv|prolongad|larg[oa]\b|por encima|superior|(mayor|más) (de lo|que)"
BAJO = r"\bbaj[oa]s?\b|pocos?\s+(minutos|tiempo|pasos)|poca\b|cort[oa]\b|breve|inferior|por debajo|(menor|menos) (de lo|que)"
# Ajuste posterior a leer los primeros resultados: frase que presenta como BUENO o ÚTIL algo que el payload marca como factor que SUBE el riesgo
POSITIVO = r"lo (cual|que) (suele|puede) ayudar|lo cual es (bueno|positivo)|es (bueno|buena|positivo|positiva)|ayuda a mejorar el sue|ayuda a dormir mejor"
DIAG = r"diagn[oó]stic|insomnio|apnea|depresi[oó]n|ansiedad|trastorno|enfermedad|patolog|s[ií]ndrome|narcolepsia|hipertensi[oó]n|cardiopat"
NEG_DIAG = r"no (es|son|constituye|constituyen|se trata de|reemplaza|reemplazan|sustituye)[^.]{0,25}diagn[oó]stic\w*"
MED = r"medicamento|medicaci[oó]n|pastilla|f[aá]rmaco|melatonina|somn[ií]fero|suplemento|ansiol[ií]tico|antidepresiv|c[aá]psula|dosis"
CAUSA = r"debido a|a causa de|por culpa de|es la causa|causad[oa]s? por|se debe a|te (est[aá] )?(provoca|causa|produce)|provoca|ocasiona"
NIVEL = r"(?:riesgo|nivel)\s+(?:de\s+)?(leve|moderado|alto|bajo|medio|elevado)"
NIVEL_MAP = {"leve": "Leve", "bajo": "Leve", "moderado": "Moderado", "medio": "Moderado", "alto": "Alto", "elevado": "Alto"}
ES_WORDS = set("el la los las de del que y en un una es con para por se su tu te no al lo como más pero sus si ya muy también puedes podría hoy noche noches sueño nivel riesgo".split())
EN_WORDS = set("the and of to is are you your with for that this it as be on can may could should sleep level risk tonight today".split())


# ---------------------------------------------------------------- payload -> lo que ve el LLM
def llm_view(payload, condition):
    """Vista del payload que recibe el LLM. Sin student_id (no se envían datos que identifiquen)."""
    view = {"nivel_de_riesgo": payload["risk_level"]}
    if condition == "C2":  # factores ya verbalizados por código: el sentido (por encima/por debajo, sube/baja) NO lo interpreta el LLM
        def frase(x):
            d = (x["person_value"] - x["group_median"]) / max(abs(x["group_median"]), 1e-9)
            pos = "por encima de lo típico" if d > 0.03 else ("por debajo de lo típico" if d < -0.03 else "cerca de lo típico")
            return (f"{VARIABLE_LABELS[x['main_variable']]}: {x['person_value']} frente a {x['group_median']} típico ({pos}). "
                    f"Este factor {'SUBE' if x['direction'].startswith('sube') else 'BAJA'} el riesgo.")
        view["factores_que_suben_el_riesgo"] = [frase(x) for x in payload["risk_factors"]]
        view["factor_que_baja_el_riesgo"] = [frase(x) for x in payload["protective_factor"]]
        view["noches_con_datos"] = payload["data_quality"]["nights_with_sleep_data"]
        view["nota"] = payload["explanation_note"] + " Cada frase ya indica si el valor está por encima o por debajo de lo típico y si el factor sube o baja el riesgo: no cambies ese sentido."
    if condition == "C1":  # con factores SHAP
        def f(x):
            return {"factor": x["group"], "variable_principal": VARIABLE_LABELS[x["main_variable"]],
                    "efecto": x["direction"], "valor_del_estudiante": x["person_value"], "valor_tipico": x["group_median"]}
        view["factores_que_suben_el_riesgo"] = [f(x) for x in payload["risk_factors"]]
        view["factor_que_baja_el_riesgo"] = [f(x) for x in payload["protective_factor"]]
        view["noches_con_datos"] = payload["data_quality"]["nights_with_sleep_data"]
        view["nota"] = payload["explanation_note"]
    return view


def build_messages(payload, condition):
    import json
    user = "Datos del estudiante:\n" + json.dumps(llm_view(payload, condition), ensure_ascii=False, indent=1)
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


# ---------------------------------------------------------------- adaptadores (misma interfaz)
class LocalGGUF:
    """Modelo abierto ejecutado en la PC del equipo con llama.cpp (los datos no salen del equipo)."""

    def __init__(self, name, path, n_ctx=4096, max_tokens=220, temperature=0.3, seed=42, strip_think=False):
        from llama_cpp import Llama
        self.name, self.max_tokens, self.temperature, self.strip_think = name, max_tokens, temperature, strip_think
        self.llm = Llama(model_path=os.path.expanduser(path), n_ctx=n_ctx, n_gpu_layers=0, n_threads=8, verbose=False, seed=seed)

    def generate(self, messages):
        t0 = time.time()
        r = self.llm.create_chat_completion(messages=messages, max_tokens=self.max_tokens, temperature=self.temperature, top_p=0.9)
        text = r["choices"][0]["message"]["content"] or ""
        finished = r["choices"][0].get("finish_reason") == "stop"
        if self.strip_think:
            if "</think>" in text:
                text = text.split("</think>", 1)[1]
            else:                      # se acabó el presupuesto de tokens pensando: no hay respuesta final
                text, finished = "", False
        return {"text": text.strip(), "seconds": round(time.time() - t0, 2),
                "tokens": r["usage"]["completion_tokens"], "finished": finished}


class AzureOpenAIAdapter:
    """Servicio administrado (Azure OpenAI). No se ejecutó en este PoC: requiere credenciales del equipo.
    Variables de entorno: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION."""

    def __init__(self, name="gpt-azure", max_tokens=220, temperature=0.3):
        from openai import AzureOpenAI
        self.name, self.max_tokens, self.temperature = name, max_tokens, temperature
        self.client = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"],
                                  api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"))
        self.deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    def generate(self, messages):
        t0 = time.time()
        r = self.client.chat.completions.create(model=self.deployment, messages=messages, max_tokens=self.max_tokens, temperature=self.temperature)
        c = r.choices[0]
        return {"text": (c.message.content or "").strip(), "seconds": round(time.time() - t0, 2),
                "tokens": r.usage.completion_tokens, "finished": c.finish_reason == "stop"}


# ---------------------------------------------------------------- validador automático
def _groups_mentioned(text):
    return {g for g, pat in GROUP_PATTERNS.items() if re.search(pat, text, re.I)}


def validate(text, payload, condition):
    """Devuelve cada chequeo por separado. `pasa` = idioma + longitud + seguridad + nivel + (con factores) refiere un factor enviado."""
    t = (text or "").strip()
    low = t.lower()
    words = re.findall(r"\w+", low)
    n_es = sum(w in ES_WORDS for w in words); n_en = sum(w in EN_WORDS for w in words)
    idioma = len(words) > 0 and n_es >= 5 and n_es / max(n_es + n_en, 1) >= 0.8
    longitud = 0 < len(words) <= MAX_PALABRAS
    low_diag = re.sub(NEG_DIAG, "", low)
    diag = bool(re.search(DIAG, low_diag)); med = bool(re.search(MED, low)); causa = bool(re.search(CAUSA, low))
    seguro = not (diag or med or causa)
    niveles = {NIVEL_MAP[m] for m in re.findall(NIVEL, low)}
    nivel_ok = niveles <= {payload["risk_level"]}
    sent = {x["group"] for x in payload["risk_factors"] + payload["protective_factor"]}
    main = payload["risk_factors"][0]["group"] if payload["risk_factors"] else None
    mentioned = _groups_mentioned(low)
    sin_inventar = mentioned <= sent and not re.search(OTROS, low)
    # dirección invertida: una frase que habla de un factor que SUBE el riesgo y lo presenta como bueno/útil
    suben = {x["group"] for x in payload["risk_factors"]}
    invertida = any(re.search(POSITIVO, s) and (_groups_mentioned(s) & suben) for s in re.split(r"[.!?]", low))
    refiere = bool(mentioned & sent) if sent else True
    menciona_principal = (main in mentioned) if main else None
    # lectura de valores: el texto dice "alto" de un factor cuyo valor está por DEBAJO del típico (o al revés)
    contradice = False
    for x in payload["risk_factors"] + payload["protective_factor"]:
        d = (x["person_value"] - x["group_median"]) / max(abs(x["group_median"]), 1e-9)
        estado = "alto" if d > 0.03 else ("bajo" if d < -0.03 else "típico")
        if estado == "típico":
            continue
        for sent_ in re.split(r"[.!?]", low):
            if re.search(GROUP_PATTERNS[x["group"]], sent_):
                hi, lo = bool(re.search(ALTO, sent_)), bool(re.search(BAJO, sent_))
                if (estado == "bajo" and hi and not lo) or (estado == "alto" and lo and not hi):
                    contradice = True
    coherente = sin_inventar and not invertida and not contradice and (refiere if condition in ("C1", "C2") else True)
    pasa = idioma and longitud and seguro and nivel_ok and (refiere if condition in ("C1", "C2") else True)
    return {"palabras": len(words), "idioma_ok": idioma, "longitud_ok": longitud, "diagnostico": diag, "medicacion": med,
            "causa_afirmada": causa, "seguro": seguro, "nivel_ok": nivel_ok, "sin_factores_inventados": sin_inventar, "direccion_invertida": invertida, "contradice_valor": contradice,
            "refiere_factor_enviado": refiere, "menciona_factor_principal": menciona_principal, "coherente": coherente, "pasa": pasa}


# ---------------------------------------------------------------- respaldo (sin LLM)
ACCION = {
    "Duración y eficiencia del sueño": "Hoy puedes intentar acostarte un poco antes para ganar unos minutos de sueño.",
    "Regularidad del sueño (variación entre noches)": "Hoy puedes intentar acostarte y levantarte cerca de tu hora habitual.",
    "Frecuencia cardíaca y HRV": "Hoy puedes probar unos minutos de respiración lenta antes de dormir.",
    "Respiración y oxígeno": "Hoy puedes cuidar que tu habitación esté ventilada al dormir.",
    "Actividad y sedentarismo": "Hoy puedes intentar hacer una caminata corta o pausas activas.",
}
FACTOR_TXT = {
    "Duración y eficiencia del sueño": "la duración y la eficiencia de tu sueño",
    "Regularidad del sueño (variación entre noches)": "la variación de tu sueño entre noches",
    "Frecuencia cardíaca y HRV": "tu frecuencia cardíaca y su variabilidad",
    "Respiración y oxígeno": "tu respiración y tu oxígeno durante el sueño",
    "Actividad y sedentarismo": "tu nivel de actividad y sedentarismo",
}


def fallback(payload):
    lvl = payload["risk_level"]
    if payload["risk_factors"]:
        g = payload["risk_factors"][0]["group"]
        return (f"Tu nivel de riesgo estimado es {lvl}. Lo que más se asocia a este resultado es {FACTOR_TXT[g]}. {ACCION[g]} "
                "Esta orientación no es un diagnóstico." + (" Si quieres, conversa con bienestar universitario." if lvl == "Alto" else ""))
    if payload["protective_factor"]:   # solo hay factor protector (la primera versión de la plantilla no lo mencionaba y el validador la rechazaba en 8 de 37 casos)
        g = payload["protective_factor"][0]["group"]
        return (f"Tu nivel de riesgo estimado es {lvl}. Ningún factor destaca por subir tu riesgo, y {FACTOR_TXT[g]} se asocia con un riesgo menor. "
                "Hoy puedes seguir con tu rutina de siempre. Esta orientación no es un diagnóstico.")
    return (f"Tu nivel de riesgo estimado es {lvl}. Por ahora no hay un factor que destaque en tus datos. "
            "Hoy puedes seguir con tu rutina de siempre. Esta orientación no es un diagnóstico.")
