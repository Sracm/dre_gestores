import sqlite3
from collections import OrderedDict

conn = sqlite3.connect("dre_cache.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT
        bloco,
        titulo,
        descrnat,
        SUM(realizado) AS realizado,
        SUM(orcado) AS orcado
    FROM dre_data
    WHERE ano = 2026 AND mes = 8
    GROUP BY bloco, titulo, descrnat
    ORDER BY bloco, titulo, descrnat
""")
rows = [dict(r) for r in cur.fetchall()]

# Check titles with bonif
bonif_rows = [r for r in rows if "bonif" in (r["titulo"] or "").lower()]
print(f"Bonif rows count: {len(bonif_rows)}")
for r in bonif_rows[:5]:
    print(" ", r)

# Sum of bonif
bonif_total = sum(float(r.get("realizado") or 0) for r in bonif_rows)
print(f"Bonif total: R$ {bonif_total:,.2f}")

conn.close()
