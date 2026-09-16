import sqlite3

conn = sqlite3.connect('dre_cache.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Verificar na dre_detalhe_fsp especificamente para o cencus 10020000
cur.execute("""
    SELECT codcencus, ano, mes, bloco, titulo, descrnat, parceiro, orcado, realizado
    FROM dre_detalhe_fsp
    WHERE descrnat LIKE '%DESP FCC COMERCIAL%'
    AND ano = 2026
    ORDER BY mes
""")
rows = cur.fetchall()
print(f"=== dre_detalhe_fsp: DESP FCC COMERCIAL (todos codcencus) ===")
print(f"Total: {len(rows)}")
for r in rows:
    print(f"  codcencus={r['codcencus']} | mes={r['mes']} | orc={r['orcado']} | real={r['realizado']} | titulo={r['titulo']}")

print()

# Verificar o que tem no CENCUS 10020000 para o mes 9
cur.execute("""
    SELECT codcencus, titulo, descrnat, SUM(CAST(orcado AS REAL)) as orc, SUM(CAST(realizado AS REAL)) as real
    FROM dre_detalhe_fsp
    WHERE codcencus = 10020000 AND ano = 2026 AND mes = 9
    GROUP BY titulo, descrnat
    ORDER BY titulo, descrnat
""")
rows2 = cur.fetchall()
print(f"=== dre_detalhe_fsp: CENCUS 10020000, mes=9, 2026 ===")
for r in rows2:
    print(f"  titulo={r['titulo']} | descr={r['descrnat']} | orc={r['orc']} | real={r['real']}")

print()
# Verificar se existe DESP FCC COMERCIAL em qualquer cencus com realizado != 0
cur.execute("""
    SELECT codcencus, titulo, descrnat, SUM(CAST(orcado AS REAL)) as orc, SUM(CAST(realizado AS REAL)) as real
    FROM dre_detalhe_fsp
    WHERE descrnat LIKE '%DESP FCC COMERCIAL%' AND ano = 2026 AND mes = 9
    GROUP BY codcencus, titulo, descrnat
""")
rows3 = cur.fetchall()
print(f"=== DESP FCC COMERCIAL em setembro 2026 ===")
for r in rows3:
    print(f"  codcencus={r['codcencus']} | titulo={r['titulo']} | orc={r['orc']} | real={r['real']}")

conn.close()
