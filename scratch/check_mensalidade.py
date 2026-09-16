import sqlite3
import pandas as pd

conn = sqlite3.connect('dre_cache.db')
df = pd.read_sql("SELECT descrnat, sum(realizado) as real, sum(orcado) as orc FROM dre_data WHERE LOWER(descrnat) LIKE '%mensalidade%' AND ano = 2026 AND mes = 8 GROUP BY descrnat", conn)
print(df)
