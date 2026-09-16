import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for page_name, visuals in data.items():
    print(f"PAGE: {page_name}")
    for v in visuals:
        v_type = v.get("type")
        v_id = v.get("id")
        if v_type in ["pivotTable", "tableEx"]:
            print(f"  Matrix ID: {v_id}")
            proj = v.get("projections", {})
            for pk, pv in proj.items():
                refs = [p.get("queryRef") for p in pv.get("projections", [])]
                print(f"    Projection {pk}: {refs}")
            flts = v.get("filters", {}).get("filters", [])
            print(f"    Visual Filters count: {len(flts)}")
            for i, flt in enumerate(flts):
                print(f"      Filter {i}: {json.dumps(flt)}")

print("\n-----------------------------------------------\n")
