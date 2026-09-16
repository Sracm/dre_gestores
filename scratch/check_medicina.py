import sqlite3

conn = sqlite3.connect('dre_cache.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- dre_detalhe_rh: MEDICINA DO TRABALHO por mes em 2026 ---")
cur.execute("""
    SELECT mes, nomemes, parceiro, orcado, realizado
    FROM dre_detalhe_rh
    WHERE ano = 2026 AND descrnat LIKE '%MEDICINA DO TRABALHO%'
    ORDER BY mes, parceiro
""")
rows = cur.fetchall()
for r in rows:
    print(f"Mes {r['mes']:02d} ({r['nomemes']}): Parc='{r['parceiro']}' | Orc={r['orcado']} | Real={r['realizado']}")

print("\n--- dre_data: MEDICINA DO TRABALHO por mes em 2026 (RH) ---")
cur.execute("""
    SELECT mes, descrnat, orcado, realizado
    FROM dre_data
    WHERE ano = 2026 AND codcencus = 9010000 AND descrnat LIKE '%MEDICINA DO TRABALHO%'
    ORDER BY mes
""")
for r in cur.fetchall():
    print(f"Mes {r['mes']:02d}: Desc='{r['descrnat']}' | Orc={r['orcado']} | Real={r['realizado']}")

conn.close()
