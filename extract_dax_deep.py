import zipfile
import re
import os

pbix_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ. GESTORES .2.1.pbix"

with zipfile.ZipFile(pbix_path, 'r') as z:
    dm_bytes = z.read("DataModel")

print(f"DataModel size: {len(dm_bytes):,} bytes")

# Extract all ASCII strings of length >= 6
pattern = re.compile(rb'[\x20-\x7e\t\r\n]{6,}')
ascii_strings = [m.group(0).decode('ascii', errors='ignore') for m in pattern.finditer(dm_bytes)]

# Extract all UTF-16LE strings
pattern16 = re.compile(rb'(?:[\x20-\x7e\t\r\n]\x00){6,}')
utf16_strings = [m.group(0).decode('utf-16le', errors='ignore') for m in pattern16.finditer(dm_bytes)]

all_strings = ascii_strings + utf16_strings
print(f"Extracted {len(all_strings):,} text blocks.")

dax_keywords = ["CALCULATE", "DIVIDE", "SUM(", "SUMX", "SWITCH", "BLANK", "COALESCE", "VAR ", "RETURN", "TOTAL MATRIZ", "Margem", "REALIZADO", "ORCADO", "ORÇADO"]

found = []
for s in all_strings:
    matches = sum(1 for kw in dax_keywords if kw in s.upper())
    if matches >= 2 and len(s) > 25:
        found.append(s.strip())

# Deduplicate
unique_found = []
seen = set()
for f in found:
    # normalize whitespace
    norm = " ".join(f.split())
    if norm not in seen:
        seen.add(norm)
        unique_found.append(f)

print(f"Found {len(unique_found)} potential DAX / M formula blocks.")
with open("extracted_dax_all.txt", "w", encoding="utf-8") as out:
    for i, u in enumerate(unique_found):
        out.write(f"\n--- BLOCK {i+1} ---\n{u}\n")

print("Saved to extracted_dax_all.txt")
