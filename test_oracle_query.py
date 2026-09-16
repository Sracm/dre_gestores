import oracledb
import time

print("Conectando ao Oracle 192.168.1.55/ORCL...")
t0 = time.time()
conn = oracledb.connect(user="sankhya", password="mqh41r", dsn="192.168.1.55/ORCL")
print(f"Conectado em {time.time()-t0:.2f}s")

cur = conn.cursor()

# Testando query simples na VMQ_DREQLIK com DTCOMP em 2026
print("Testando contagem de registros em VMQ_DREQLIK com DTCOMP >= 2026-01-01...")
t0 = time.time()
cur.execute("""
    SELECT COUNT(*) FROM VMQ_DREQLIK
    WHERE DTCOMP >= TO_DATE('2026-01-01', 'YYYY-MM-DD')
""")
total_2026 = cur.fetchone()[0]
print(f"Total 2026: {total_2026} registros em {time.time()-t0:.2f}s")

cur.close()
conn.close()
