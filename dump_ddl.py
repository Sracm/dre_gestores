import oracledb

DB_USER = "sankhya"
DB_PASS = "mqh41r"
DB_DSN = "192.168.1.55/ORCL"

conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cursor = conn.cursor()

cursor.execute("SELECT TEXT FROM ALL_VIEWS WHERE VIEW_NAME = 'VMQ_DREQLIK'")
row = cursor.fetchone()
if row:
    with open("vmq_dreqlik_ddl.sql", "w", encoding="utf-8") as f:
        f.write(row[0])
    print("Wrote vmq_dreqlik_ddl.sql (bytes:", len(row[0]), ")")
else:
    print("View not found!")

cursor.close()
conn.close()
