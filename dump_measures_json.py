import json

with open("dre_exact_measures.json", "r", encoding="utf-8-sig") as f:
    measures = json.load(f)

with open("all_measures_clean.txt", "w", encoding="utf-8") as out:
    out.write(f"Total measures: {len(measures)}\n")
    for m in measures:
        name = m.get("Measure")
        tbl = m.get("Table")
        expr = m.get("Expression", "")
        out.write(f"\n==========================================\n")
        out.write(f"TABLE: {tbl} | MEASURE: {name}\n")
        out.write(f"EXPR:\n{expr}\n")

print("Saved all_measures_clean.txt successfully!")
