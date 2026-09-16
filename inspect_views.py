import oracledb

conn = oracledb.connect(user="sankhya", password="mqh41r", dsn="192.168.1.55/ORCL")
cur = conn.cursor()

for table in ["VMQ_CADDRE", "VMQ_TSICUS", "VMQ_TGFNAT", "VMQ_TSIEMP"]:
    cur.execute(f"SELECT * FROM {table} WHERE ROWNUM <= 2")
    cols = [c[0] for c in cur.description]
    print(f"\nTABLE {table}: {cols}")
    rows = cur.fetchall()
    for r in rows:
        print("  Sample row:", r)

cur.close()
conn.close()
