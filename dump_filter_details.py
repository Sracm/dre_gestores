import json

with open("visuals_detailed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("filter_details.txt", "w", encoding="utf-8") as out:
    for v in data.get("DRE GESTORES", []):
        if v.get("id") == "688f961a41b2f82056d0":
            filters = v.get("filters", {}).get("filters", [])
            for i, flt in enumerate(filters):
                out.write(f"=== Filter {i} ===\n")
                out.write(json.dumps(flt, indent=2) + "\n")

print("Saved filter_details.txt")
