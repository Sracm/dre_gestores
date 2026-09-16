import zipfile
import re
import os
import sys

sys.stdout.reconfigure(line_buffering=True)

pbix_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ. GESTORES .2.1.pbix"

with zipfile.ZipFile(pbix_path, 'r') as z:
    dm_bytes = z.read("DataModel")

print(f"DataModel size: {len(dm_bytes):,} bytes")

# Extract printable strings and look for DAX measures and table names
# In SSAS tabular, measure expressions are stored in utf-16 or utf-8 strings
strings = set()
# Search for M queries and DAX expressions
# Common DAX functions: CALCULATE, SUM, DIVIDE, FILTER, ALL, ALLEXCEPT, DATESYTD, etc.
pattern = re.compile(rb'[\x20-\x7e]{4,}')
found_dax = []

# Also let's search for visual configurations in the extracted Report/definition
for root, dirs, files in os.walk("pbix_extracted"):
    for file in files:
        if file.endswith(".json"):
            fp = os.path.join(root, file)
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Check for measure names / expressions
                matches = re.findall(r'"(?:Measure|Property|Column|Entity)":\s*"([^"]+)"', content)
                if matches:
                    strings.update(matches)

print("\nEntities and Measures referenced in Report Visuals:")
for s in sorted(strings):
    print("  ", s)
