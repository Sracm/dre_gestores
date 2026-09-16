import json

with open("dre_tabular_model_full.json", "r", encoding="utf-8-sig") as f:
    model = json.load(f)

print("=== RELATIONSHIPS ===")
for r in model.get("Relationships", []):
    print(f"  {r['FromTable']}[{r['FromColumn']}]  -->  {r['ToTable']}[{r['ToColumn']}] (Active: {r['IsActive']}, CrossFilter: {r['CrossFilteringBehavior']})")

print("\n=== CALCULATED COLUMNS ===")
for t in model.get("Tables", []):
    tname = t["Name"]
    for c in t["Columns"]:
        if c.get("Type") == "Calculated":
            print(f"  [{tname}] {c['Name']} = {c.get('Expression')}")

print("\n=== CALCULATED TABLES / M QUERIES ===")
for t in model.get("Tables", []):
    tname = t["Name"]
    for p in t["Partitions"]:
        if p.get("SourceType") == "Calculated":
            print(f"\n[Calculated Table: {tname}]\nDAX = {p.get('Query')}")
        elif tname in ["bonifChave", "Margem de Contribuição", "Consulta1"]:
            print(f"\n[Table: {tname}] M Query:\n{p.get('Query')}")
