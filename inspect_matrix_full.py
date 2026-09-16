import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data.get("DRE GESTORES", []):
    v_type = v.get("type")
    v_id = v.get("id")
    if v_type in ["pivotTable", "tableEx"]:
        print(f"Visual ID: {v_id}, Type: {v_type}")
        projections = v.get("projections", {})
        for pk, pv in projections.items():
            fields = [p.get('queryRef') for p in pv.get('projections', [])]
            print(f"  {pk}: {fields}")
        print("\nFILTERS:")
        print(json.dumps(v.get("filters", {}), indent=2))
