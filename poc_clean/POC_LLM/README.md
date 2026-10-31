# PoC del LLM (recomendaciones a partir del nivel y los factores SHAP)

Notebook: [`POC_LLM.ipynb`](POC_LLM.ipynb) (ejecutado, con resultados). Se comparan tres condiciones: **C0** solo el nivel, **C1** nivel + factores SHAP con valores crudos (el diseño), **C2** igual que C1 pero con cada factor verbalizado por código.

| Archivo | Qué es |
|---|---|
| `generar_payloads.py` | Reusa las celdas de `../POC_FINAL/POC_Final_SHAP.ipynb` y guarda `payloads_37.json` (los 37 payloads, sin metodología nueva). |
| `llm_lib.py` | Prompt v1, vista del payload por condición, adaptadores (`LocalGGUF`, `AzureOpenAIAdapter`), validador, plantilla de respaldo. |
| `generar.py` | Genera y guarda `generaciones.jsonl` (reanudable). Gemma 3 4B en las 37 personas; DeepSeek-R1-Distill 7B en 8 (es lento en CPU). |
| `resultados_llm.json` | Puntajes 1–5 del benchmark y comparaciones C0/C1/C2. |
| `evaluacion_experta_muestra.csv` / `_CLAVE.csv` | Hoja **ciega** para la evaluación experta (pendiente) y su clave. |
| `PROMPT_NOTEBOOKLM.md` | Prompt para completar las fuentes del informe (marcas amarillas `[FUENTE: …]`). |

**Dependencias:** las del proyecto + `llama-cpp-python` (rueda CPU: `pip install llama-cpp-python --only-binary=:all: --index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`). Los modelos son los GGUF descargados en LM Studio (`~/.lmstudio/models/...`).

**No se ejecutó GPT en Azure OpenAI** (faltan credenciales): correr `AzureOpenAIAdapter` con las variables `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`. Tampoco se hizo la evaluación experta.
