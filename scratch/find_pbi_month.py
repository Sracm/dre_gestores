import sqlite3

conn = sqlite3.connect('dre_cache.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Procura por mes/ano onde Margem = -145697 ou 1.Despesas = -18069 ---")
cur.execute("""
    SELECT ano, mes, nomemes, 
           SUM(orcado) as orcado_total, 
           SUM(realizado) as realizado_total
    FROM dre_detalhe_rh
    GROUP BY ano, mes, nomemes
    ORDER BY ano, mes
""")
for r in cur.fetchall():
    print(f"Ano {r['ano']} | Mes {r['mes']:02d} ({r['nomemes']}) | Orcado: {r['orcado_total']:,.2f} | Realizado: {r['realizado_total']:,.2f}")

print("\n--- Procura especificamente 1.Despesas Administrativas por mes/ano ---")
cur.execute("""
    SELECT ano, mes, nomemes, 
           SUM(orcado) as orcado_desp, 
           SUM(realizado) as realizado_desp
    FROM dre_detalhe_rh
    WHERE titulo LIKE '%1.Despesas Administrativas%'
    GROUP BY ano, mes, nomemes
    ORDER BY ano, mes
""")
for r in cur.fetchall():
    print(f"Ano {r['ano']} | Mes {r['mes']:02d} ({r['nomemes']}) | 1.Desp Orc: {r['orcado_desp']:,.2f} | 1.Desp Real: {r['realizado_desp']:,.2f}")

conn.close()
