import sqlite3
import pandas as pd

conn = sqlite3.connect("dre_cache.db")

allowed_companies = [
    'Consolidação', 'FORX', 'MCR - FABRICA', 'MCR - FILIAL 03', 
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ', 
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]
companies_str = ",".join([f"'{c}'" for c in allowed_companies])

sql = f"""
SELECT 
    bloco,
    titulo,
    SUM(realizado) as real,
    SUM(orcado) as orc
FROM dre_data
WHERE ano = 2026 AND mes = 3
  AND empresa IN ({companies_str})
  AND codcencus != 21010000
GROUP BY bloco, titulo
ORDER BY bloco, titulo
"""

df = pd.read_sql_query(sql, conn)
print("=== DRE DATA WITH EXACT FILTERS (MARÇO/2026) ===")
for _, r in df.iterrows():
    print(f"{r['bloco']:<35} | {r['titulo']:<35} | Real: {r['real']:>14,.2f} | Orc: {r['orc']:>14,.2f}")

# Totals by bloco
print("\n=== TOTAIS POR BLOCO ===")
df_bloco = df.groupby("bloco")[["real", "orc"]].sum().reset_index()
for _, r in df_bloco.iterrows():
    print(f"{r['bloco']:<35} | Real: {r['real']:>14,.2f} | Orc: {r['orc']:>14,.2f}")

conn.close()
