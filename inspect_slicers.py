import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data.get("DRE GESTORES", []):
    if v.get("type") == "slicer":
        print(f"\nSLICER ID: {v.get('id')}")
        print("Projections:", v.get("projections"))
        print("Filters:", json.dumps(v.get("filters"), indent=2))
        print("Objects / Config:")
        print(json.dumps(v.get("objects", {}), indent=2))
