import json

with open("dre_exact_measures.json", "r", encoding="utf-8-sig") as f:
    measures = json.load(f)

for m in measures:
    name = m.get("Measure")
    if any(k in name.lower() for k in ["teste", "realizado", "orcado", "antonio"]):
        print(f"=== MEASURE: {name} (Table: {m.get('Table')}) ===")
        print(m.get("Expression"))
        print()
