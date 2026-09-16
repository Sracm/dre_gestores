import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for page_name, visuals in data.items():
    print(f"\n========================================================")
    print(f"PAGE: {page_name}")
    print(f"========================================================")
    for v in visuals:
        vtype = v["type"]
        if vtype in ["shape", "image", "textbox"]:
            continue
        print(f"\n--- [{vtype}] ID: {v['id']} ---")
        projs = v.get("projections", {})
        for bucket, pinfo in projs.items():
            print(f"  Bucket '{bucket}':")
            for item in pinfo.get("projections", []):
                field = item.get("field", {})
                col = field.get("Column", {}).get("Property")
                meas = field.get("Measure", {}).get("Property")
                src = field.get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity") or \
                      field.get("Measure", {}).get("Expression", {}).get("SourceRef", {}).get("Entity")
                name = item.get("displayName") or col or meas
                print(f"    - {name} (Source: {src}.{col or meas})")
        
        # Filters
        fconf = v.get("filters", {})
        if isinstance(fconf, dict) and "filters" in fconf:
            print("  Visual-level Filters:")
            for flt in fconf.get("filters", []):
                field = flt.get("field", {})
                col = field.get("Column", {}).get("Property")
                src = field.get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity")
                # values
                where = flt.get("filter", {}).get("Where", [])
                vals = []
                for w in where:
                    for vlist in w.get("Condition", {}).get("In", {}).get("Values", []):
                        for lit in vlist:
                            vals.append(lit.get("Literal", {}).get("Value"))
                print(f"    - Field: {src}.{col} IN {vals}")
