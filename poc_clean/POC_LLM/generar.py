"""Genera las recomendaciones del PoC (modelo x condición x persona) y las guarda en generaciones.jsonl.
Es reanudable: salta lo que ya está guardado. Uso:  python generar.py [--prueba]
Condiciones: C0 = solo el nivel (sin factores); C1 = nivel + factores SHAP con los valores crudos (el diseño de HapSleep); C2 = igual que C1 pero con cada factor ya verbalizado por código (por encima/por debajo, sube/baja).
"""
import json, sys, time
from pathlib import Path
from llm_lib import LocalGGUF, build_messages, PROMPT_VERSION

HERE = Path(__file__).resolve().parent
OUT = HERE / "generaciones.jsonl"
payloads = json.loads((HERE / "payloads_37.json").read_text(encoding="utf-8"))
ids_by_level = {}
for pid, p in sorted(payloads.items()):
    ids_by_level.setdefault(p["risk_level"], []).append(pid)
# muestra de 8 personas para el modelo lento (1 Leve, 3 Moderado, 4 Alto), fija y reproducible
SAMPLE8 = ids_by_level["Leve"][:1] + ids_by_level["Moderado"][:3] + ids_by_level["Alto"][:4]

MODELS = [
    ("gemma-3-4b", dict(path="~/.lmstudio/models/lmstudio-community/gemma-3-4B-it-qat-GGUF/gemma-3-4B-it-QAT-Q4_0.gguf",
                        max_tokens=220), sorted(payloads), ("C0", "C1", "C2")),
    ("deepseek-r1-distill-qwen-7b", dict(path="~/.lmstudio/models/lmstudio-community/DeepSeek-R1-Distill-Qwen-7B-GGUF/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
                                         max_tokens=1000, strip_think=True), SAMPLE8, ("C0", "C1")),
]

done = set()
if OUT.exists():
    for line in OUT.read_text(encoding="utf-8").splitlines():
        r = json.loads(line); done.add((r["model"], r["condition"], r["student_id"]))

test = "--prueba" in sys.argv
for name, kw, pids, conds in MODELS:
    if test:
        pids = pids[:2]
    todo = [(c, pid) for pid in pids for c in conds if (name, c, pid) not in done]
    if not todo:
        continue
    print(f"== {name}: {len(todo)} generaciones", flush=True)
    m = LocalGGUF(name, **kw)
    for k, (c, pid) in enumerate(todo, 1):
        res = m.generate(build_messages(payloads[pid], c))
        rec = {"model": name, "condition": c, "student_id": pid, "level": payloads[pid]["risk_level"], "prompt_version": PROMPT_VERSION, **res}
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{k}/{len(todo)}] {name} {c} {payloads[pid]['risk_level']} {res['seconds']}s {res['tokens']}tok fin={res['finished']}", flush=True)
    del m
