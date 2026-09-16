import json
import os

pages = {
    "DRE GESTORES": r"pbix_extracted\Report\definition\pages\9b383df7433c736a312d\visuals",
    "DRE DETALHE": r"pbix_extracted\Report\definition\pages\2874193a146931f82491\visuals"
}

for pname, pdir in pages.items():
    print(f"\n========================================================")
    print(f"PAGE: {pname}")
    print(f"========================================================")
    for vname in os.listdir(pdir):
        vf = os.path.join(pdir, vname, "visual.json")
        if not os.path.exists(vf):
            continue
        with open(vf, "r", encoding="utf-8") as f:
            vdata = json.load(f)
            v = vdata.get("visual", {})
            vtype = v.get("visualType")
            print(f"\n--- Visual: {vname} (Type: {vtype}) ---")
            
            # Print title if present
            title = v.get("visualContainerConfig", {})
            # Query / Projections / DataTransforms
            query = v.get("query", {})
            projections = query.get("queryState", {})
            if projections:
                print("  Projections:", json.dumps(projections, indent=2, ensure_ascii=False))
            
            # Print filters
            filters = v.get("filterConfig", {}) or vdata.get("filterConfig", {})
            if filters:
                print("  Filters:", json.dumps(filters, indent=2, ensure_ascii=False))
