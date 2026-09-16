import csv

csv_path = "dre_cube_data.csv"

# Let's inspect rows for 2026, month 8 (August) or 9 (September)
rows_2026_8 = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    if reader.fieldnames:
        reader.fieldnames = [c.replace("\ufeff", "") for c in reader.fieldnames]
    for r in reader:
        if r.get("DCALENDARIO[ANO]") == "2026" and r.get("DCALENDARIO[NUMEROMES]") == "8":
            rows_2026_8.append(r)
            if len(rows_2026_8) >= 10:
                break

print(f"Found {len(rows_2026_8)} rows for 2026-08 sample:")
for r in rows_2026_8[:5]:
    print("Empresa:", r.get("VMQ_TSIEMP[RAZAOABREV]"),
          "Bloco:", r.get("VMQ_CADDRE[BLOCO]"),
          "Titulo:", r.get("VMQ_CADDRE[TITULO]"),
          "DescrNat:", r.get("VMQ_TGFNAT[DESCRNAT]"),
          "Realizado:", r.get("[REALIZADO]"),
          "Orcado:", r.get("[ORCADO]"),
          "VB_Real:", r.get("[VB_REALIZADO]"))
