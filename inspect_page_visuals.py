import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("page_visuals_out.txt", "w", encoding="utf-8") as out:
    for v in data.get("DRE GESTORES", []):
        v_type = v.get("type")
        v_id = v.get("id")
        title = v.get("title", "")
        out.write(f"\nType: {v_type} | ID: {v_id} | Title: {title}\n")
        
        proj = v.get("projections", {})
        if proj:
            for pk, pv in proj.items():
                refs = [p.get("queryRef") for p in pv.get("projections", [])]
                out.write(f"  Projection {pk}: {refs}\n")
                
        flts = v.get("filters", {}).get("filters", [])
        if flts:
            out.write(f"  Filters ({len(flts)}):\n")
            for flt in flts:
                out.write(f"    {flt}\n")

print("Saved page_visuals_out.txt")
