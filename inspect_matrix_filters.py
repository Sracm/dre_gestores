import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data.get("DRE GESTORES", []):
    if v.get("type") in ["pivotTable", "tableEx"]:
        print(f"Matrix Visual ID: {v.get('id')}")
        filters = v.get("filters", {}).get("filters", [])
        for i, flt in enumerate(filters):
            field = flt.get("field", {})
            col = field.get("Column", {}).get("Property") or field.get("Measure", {}).get("Property")
            table = field.get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity") or field.get("Measure", {}).get("Expression", {}).get("SourceRef", {}).get("Entity")
            flt_val = flt.get("filter")
            print(f"  Filter {i}: {table}.{col} -> {flt.get('type')}")
            if flt_val:
                print(f"    Definition: {json.dumps(flt_val)}")
