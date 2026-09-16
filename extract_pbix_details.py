import zipfile
import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True)

pbix_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ. GESTORES .2.1.pbix"
out_dir = "pbix_extracted"
os.makedirs(out_dir, exist_ok=True)

with zipfile.ZipFile(pbix_path, 'r') as z:
    for n in z.namelist():
        if n.startswith("Report/") or n.startswith("DAXQueries/"):
            dest = os.path.join(out_dir, n.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(z.read(n))

print("Extracted Report & DAX files.")

# Print Pages
pages_file = os.path.join(out_dir, "Report", "definition", "pages", "pages.json")
if os.path.exists(pages_file):
    with open(pages_file, "r", encoding="utf-8") as f:
        print("\n=== PAGES LIST ===")
        print(f.read())

# Read each page.json
pages_dir = os.path.join(out_dir, "Report", "definition", "pages")
for p in os.listdir(pages_dir):
    page_json = os.path.join(pages_dir, p, "page.json")
    if os.path.exists(page_json):
        with open(page_json, "r", encoding="utf-8") as f:
            pdata = json.load(f)
            print(f"\n--- Page {p}: {pdata.get('displayName')} ---")
            visuals_dir = os.path.join(pages_dir, p, "visuals")
            if os.path.exists(visuals_dir):
                for v in os.listdir(visuals_dir):
                    vfile = os.path.join(visuals_dir, v, "visual.json")
                    if os.path.exists(vfile):
                        with open(vfile, "r", encoding="utf-8") as vf:
                            try:
                                vdata = json.load(vf)
                                vtype = vdata.get("visual", {}).get("visualType")
                                print(f"  Visual [{v}]: Type={vtype}")
                            except:
                                pass

# Read DAX Queries
for dax in ["Consulta%201.dax", "Consulta%202.dax"]:
    df = os.path.join(out_dir, "DAXQueries", dax)
    if os.path.exists(df):
        print(f"\n=== DAX QUERY: {dax} ===")
        with open(df, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
