"""Genera los payloads de las 37 personas del POC final (SHAP + niveles) para el PoC del LLM.

Reusa TAL CUAL las celdas de POC_FINAL/POC_Final_SHAP.ipynb (carga, RF leave-one-out, SHAP agrupado,
niveles y payload); no agrega metodología nueva. Salida: payloads_37.json (mismo formato que payload_examples.json).
"""
import json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINAL = HERE.parent / "POC_FINAL"
nb = json.loads((FINAL / "POC_Final_SHAP.ipynb").read_text(encoding="utf-8"))
code = {i: "".join(c["source"]) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"}
cell15 = code[15].split("order = ")[0]          # solo las definiciones, sin escribir payload_examples.json

os.chdir(FINAL)                                  # DATA_PATH es relativo a POC_FINAL
ns = {"__name__": "poc_final"}
for src in (code[1], code[5], code[7], cell15):
    exec(src, ns)
payloads = {ns["ids"][i]: ns["payload"](i) for i in range(len(ns["ids"]))}
(HERE / "payloads_37.json").write_text(json.dumps(payloads, indent=1, ensure_ascii=False), encoding="utf-8")
from collections import Counter
print(len(payloads), Counter(p["risk_level"] for p in payloads.values()))
