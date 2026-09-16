import sqlite3

conn = sqlite3.connect('dre_cache.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Ver o que o dre_data tem para cencus 10020000 no mes 8
cur.execute("""
    SELECT titulo, descrnat, SUM(orcado) as orc, SUM(realizado) as real
    FROM dre_data
    WHERE codcencus = 10020000 AND ano = 2026 AND mes = 8
    GROUP BY titulo, descrnat
    ORDER BY titulo, descrnat
""")
rows = cur.fetchall()
print(f"=== dre_data: CENCUS 10020000, mes=8, 2026 ===")
for r in rows:
    print(f"  titulo={r['titulo']} | descr={r['descrnat']} | orc={r['orc']} | real={r['real']}")

print()

# Comparar com dre_detalhe_fsp
cur.execute("""
    SELECT titulo, descrnat, SUM(CAST(orcado AS REAL)) as orc, SUM(CAST(realizado AS REAL)) as real
    FROM dre_detalhe_fsp
    WHERE codcencus = 10020000 AND ano = 2026 AND mes = 8
    GROUP BY titulo, descrnat
    ORDER BY titulo, descrnat
""")
rows2 = cur.fetchall()
print(f"=== dre_detalhe_fsp: CENCUS 10020000, mes=8, 2026 ===")
for r in rows2:
    print(f"  titulo={r['titulo']} | descr={r['descrnat']} | orc={r['orc']} | real={r['real']}")

conn.close()
