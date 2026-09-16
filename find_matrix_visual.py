import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for page_name, visuals in data.items():
    print(f"\nPage: {page_name} ({len(visuals)} visuals)")
    for v in visuals:
        v_type = v.get("type")
        v_id = v.get("id")
        projections = v.get("projections", {})
        proj_keys = list(projections.keys())
        print(f"  Visual {v_id}: type={v_type}, projections={proj_keys}")
        # If it has columns or rows
        if "Rows" in projections or "Columns" in projections or "Values" in projections:
            print(f"    Details:")
            for pk, pv in projections.items():
                fields = []
                for p in pv.get("projections", []):
                    f = p.get("field", {})
                    qref = p.get("queryRef", "")
                    fields.append(qref)
                print(f"      {pk}: {fields}")
            if v.get("filters"):
                print(f"    Filters: {v.get('filters')}")
