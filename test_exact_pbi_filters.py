import sqlite3
import pandas as pd

conn = sqlite3.connect("dre_cache.db")

allowed_companies = [
    'Consolidação', 'FORX', 'MCR - FABRICA', 'MCR - FILIAL 03', 
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ', 
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]

# Also check CODEMP <> 9, CODCENCUS <> 21010000
sql = f"""
SELECT 
    CODEMP,
    RAZAOABREV,
    CODCENCUS,
    BLOCO,
    TITULO,
    SUM(VALOR) as SOMA_VALOR,
    SUM(ORCAMENTO) as SOMA_ORC
FROM dre_base
WHERE ANO = 2026 AND MES = 'mar'
GROUP BY CODEMP, RAZAOABREV, CODCENCUS, BLOCO, TITULO
"""
df = pd.read_sql_query(sql, conn)
print(f"Total rows in Mar 2026: {len(df)}")
print("Companies in DB for Mar 2026:")
print(df["RAZAOABREV"].value_counts())

print("\n--- Now filtering allowed companies ---")
df_filtered = df[df["RAZAOABREV"].isin(allowed_companies)].copy()
# Also exclude CODEMP 9 and CODCENCUS 21010000
df_filtered = df_filtered[df_filtered["CODEMP"] != 9]
df_filtered = df_filtered[df_filtered["CODCENCUS"] != 21010000]

print("Companies remaining after filter:")
print(df_filtered["RAZAOABREV"].value_counts())

# Group by BLOCO and TITULO
g = df_filtered.groupby(["BLOCO", "TITULO"])[["SOMA_VALOR", "SOMA_ORC"]].sum().reset_index()

print("\n=== COMPARISON WITH POWER BI (FILTERED) ===")
for _, r in g.iterrows():
    print(f"{r['BLOCO']:<35} | {r['TITULO']:<35} | Real: {r['SOMA_VALOR']:>12,.2f} | Orc: {r['SOMA_ORC']:>12,.2f}")

conn.close()
