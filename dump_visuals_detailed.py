import json
import os

pages = {
    "DRE GESTORES": r"pbix_extracted\Report\definition\pages\9b383df7433c736a312d\visuals",
    "DRE DETALHE": r"pbix_extracted\Report\definition\pages\2874193a146931f82491\visuals"
}

summary = {}

for pname, pdir in pages.items():
    summary[pname] = []
    for vname in os.listdir(pdir):
        vf = os.path.join(pdir, vname, "visual.json")
        if not os.path.exists(vf):
            continue
        with open(vf, "r", encoding="utf-8") as f:
            vdata = json.load(f)
            v = vdata.get("visual", {})
            vtype = v.get("visualType")
            projections = v.get("query", {}).get("queryState", {})
            filters = v.get("filterConfig", {}) or vdata.get("filterConfig", {})
            
            summary[pname].append({
                "id": vname,
                "type": vtype,
                "projections": projections,
                "filters": filters
            })

with open("visuals_detailed.json", "w", encoding="utf-8") as out:
    json.dump(summary, out, indent=2, ensure_ascii=False)

print("Saved visuals_detailed.json successfully!")
