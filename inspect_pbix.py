import zipfile
import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True)

pbix_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ. GESTORES .2.1.pbix"

if not os.path.exists(pbix_path):
    print(f"File not found: {pbix_path}")
    sys.exit(1)

print(f"Opening PBIX: {pbix_path}")
print(f"Size: {os.path.getsize(pbix_path) / (1024*1024):.2f} MB")

with zipfile.ZipFile(pbix_path, 'r') as z:
    names = z.namelist()
    print("\nFiles in PBIX:")
    for n in names:
        info = z.getinfo(n)
        print(f"  {n} ({info.file_size:,} bytes)")

    # Check DataModelSchema if exists
    if "DataModelSchema" in names:
        print("\n--- Reading DataModelSchema ---")
        schema_bytes = z.read("DataModelSchema")
        # May be utf-16 le
        for enc in ['utf-16-le', 'utf-8']:
            try:
                schema_json = json.loads(schema_bytes.decode(enc))
                print("Decoded DataModelSchema successfully!")
                with open("schema.json", "w", encoding="utf-8") as out:
                    json.dump(schema_json, out, indent=2, ensure_ascii=False)
                print("Saved schema.json")
                break
            except Exception as e:
                pass

    # Check Layout
    if "Report/Layout" in names:
        print("\n--- Reading Report/Layout ---")
        layout_bytes = z.read("Report/Layout")
        for enc in ['utf-16-le', 'utf-8']:
            try:
                layout_json = json.loads(layout_bytes.decode(enc))
                print("Decoded Report/Layout successfully!")
                with open("layout.json", "w", encoding="utf-8") as out:
                    json.dump(layout_json, out, indent=2, ensure_ascii=False)
                print("Saved layout.json")
                break
            except Exception as e:
                pass
