import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data.get("DRE GESTORES", []):
    v_type = v.get("type")
    v_id = v.get("id")
    if v_type in ["pivotTable", "tableEx"]:
        print(f"\nFound Matrix/Table in DRE GESTORES:")
        print(f"  ID: {v_id}, Type: {v_type}")
        print("  Projections:")
        for pk, pv in v.get("projections", {}).items():
            print(f"    {pk}: {[p.get('queryRef') for p in pv.get('projections', [])]}")
        print("  Filters:")
        print(json.dumps(v.get("filters", {}), indent=2))
