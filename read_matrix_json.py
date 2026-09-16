import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("pbi_setup_clean.txt", "w", encoding="utf-8") as out:
    for page_name, visuals in data.items():
        out.write(f"PAGE: {page_name}\n")
        for v in visuals:
            v_type = v.get("type")
            v_id = v.get("id")
            if v_type in ["pivotTable", "tableEx"]:
                out.write(f"  Matrix ID: {v_id}\n")
                proj = v.get("projections", {})
                for pk, pv in proj.items():
                    refs = [p.get("queryRef") for p in pv.get("projections", [])]
                    out.write(f"    Projection {pk}: {refs}\n")
                flts = v.get("filters", {}).get("filters", [])
                out.write(f"    Visual Filters count: {len(flts)}\n")
                for i, flt in enumerate(flts):
                    out.write(f"      Filter {i}: {json.dumps(flt)}\n")
