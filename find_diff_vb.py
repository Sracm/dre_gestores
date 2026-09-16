import sqlite3
import pandas as pd

conn = sqlite3.connect("dre_cache.db")

allowed_companies = [
    'Consolidação', 'FORX', 'MCR - FABRICA', 'MCR - FILIAL 03', 
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ', 
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]

# Let's inspect the tables in dre_cache.db
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("Tables in dre_cache.db:", tables["name"].tolist())

main_table = tables["name"].tolist()[0]
print("Using table:", main_table)

df = pd.read_sql_query(f"""
SELECT * 
FROM {main_table} 
WHERE ANO = 2026 AND MES = 'mar' AND TITULO = '1.Venda Bruta'
""", conn)

df_filtered = df[df["RAZAOABREV"].isin(allowed_companies)].copy()
df_filtered = df_filtered[df_filtered["CODEMP"] != 9]
df_filtered = df_filtered[df_filtered["CODCENCUS"] != 21010000]

print("Total filtered Venda Bruta:", df_filtered["VALOR"].sum())
print("Expected Venda Bruta: 6039454.00")
print("Difference:", df_filtered["VALOR"].sum() - 6039454.00)

print("\nBreakdown by REF:")
print(df_filtered.groupby("REF")["VALOR"].sum())

print("\nBreakdown by CODCENCUS:")
print(df_filtered.groupby("CODCENCUS")["VALOR"].sum())

print("\nCheck if any CODCENCUS has ~1690:")
cencus_sum = df_filtered.groupby(["CODCENCUS", "DESCRCENCUS"])["VALOR"].sum().reset_index()
print(cencus_sum)

conn.close()
