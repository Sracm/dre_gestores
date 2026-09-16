import zipfile
import re
import os
import sys

pbix_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\DIRETORIA FINANCEIRA\DRE MQ. GESTORES .2.1.pbix"

with zipfile.ZipFile(pbix_path, 'r') as z:
    dm_bytes = z.read("DataModel")

measures_to_find = [
    "SOMA REALIZADO GESTORES",
    "SOMA REALIZADO",
    "SOMA ORCADO",
    "REALIZADO (R$)",
    "ORÇADO (R$)",
    "%s/ VB REALIZADO",
    "%s/ VB orçado",
    "MARGEM",
    "Margem de Contribuição",
    "TOTAL MATRIZ",
    "Total de Soma de valor para bloco",
    "R/O",
    "certo"
]

out_lines = []
out_lines.append(f"DataModel size: {len(dm_bytes)} bytes")

# Extract utf-16 strings
# Let's search for Expression patterns or measure formulas
# In Tabular schemas, Expression = "..."
for m in measures_to_find:
    out_lines.append(f"\n=======================================================")
    out_lines.append(f"SEARCHING FOR: {m}")
    out_lines.append(f"=======================================================")
    
    # search in both bytes (utf-16le and utf-8)
    for enc, bstr in [("utf-16le", m.encode("utf-16le")), ("utf-8", m.encode("utf-8"))]:
        idx = 0
        found_count = 0
        while True:
            pos = dm_bytes.find(bstr, idx)
            if pos == -1:
                break
            # grab surrounding 1500 bytes
            start = max(0, pos - 200)
            end = min(len(dm_bytes), pos + 1500)
            chunk = dm_bytes[start:end]
            try:
                decoded = chunk.decode(enc, errors='ignore')
                # clean control characters
                clean = "".join(c if (c.isprintable() or c in "\r\n\t") else " " for c in decoded)
                out_lines.append(f"--- Occurrence at {pos} ({enc}) ---")
                out_lines.append(clean)
                found_count += 1
            except:
                pass
            idx = pos + len(bstr) + 50
            if found_count >= 5:
                break

with open("dax_formulas.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Saved dax_formulas.txt successfully!")
