import sqlite3
import pandas as pd

conn = sqlite3.connect('dre_cache.db')
query = """
SELECT descrnat, ano, mes, parceiro, realizado, orcado 
FROM dre_detalhe_rh 
WHERE parceiro LIKE '%MENTE%' OR parceiro LIKE '%DEPPES%';
"""
df = pd.read_sql(query, conn)
print(df)
