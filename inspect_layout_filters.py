import json

with open("pbix_extracted/Report/Layout", "r", encoding="utf-16-le") as f:
    layout = json.load(f)

print("--- Report Level Filters ---")
print(layout.get("filters"))

print("\n--- Section (Page) Filters ---")
for sec in layout.get("sections", []):
    print(f"Page: {sec.get('displayName')} (name: {sec.get('name')})")
    if sec.get("filters"):
        print("  Page Filters:", sec.get("filters"))
