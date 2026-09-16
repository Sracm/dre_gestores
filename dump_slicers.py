import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("slicers_out.txt", "w", encoding="utf-8") as out:
    for v in data.get("DRE GESTORES", []):
        if v.get("type") == "slicer":
            out.write(f"\nSLICER ID: {v.get('id')}\n")
            out.write(f"Projections: {v.get('projections')}\n")
            out.write(f"Filters: {json.dumps(v.get('filters'), indent=2)}\n")
            out.write(f"Config: {v.get('config')}\n")

print("Saved slicers_out.txt")
