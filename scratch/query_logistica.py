import sqlite3

conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()
cur.execute("SELECT DISTINCT codcencus, descrcencus FROM dre_data WHERE descrcencus LIKE '%LOGISTICA%'")
print(cur.fetchall())
conn.close()
