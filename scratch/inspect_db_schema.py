import sqlite3

conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Tables in dre_cache.db:', tables)

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cur.fetchall()]
    print(f"\n{t} ({len(cols)} cols):")
    print(" ", ", ".join(cols))
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  Total rows: {cur.fetchone()[0]}")
