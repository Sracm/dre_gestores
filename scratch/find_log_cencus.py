import sqlite3

def find_cencus():
    conn = sqlite3.connect('dre_cache.db')
    conn.execute('pragma journal_mode=wal')
    cur = conn.cursor()
    # using like %LOGISTICA% to find all codcencus mapping
    cur.execute("SELECT DISTINCT codcencus, descrcencus FROM dre_data WHERE descrcencus LIKE '%LOGISTICA%'")
    rows = cur.fetchall()
    for r in rows:
        print(f"{r[0]} -> {r[1]}")
    conn.close()

find_cencus()
