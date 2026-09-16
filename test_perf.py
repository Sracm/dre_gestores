import oracledb, time

conn = oracledb.connect(user='sankhya', password='mqh41r', dsn='192.168.1.55/ORCL')
cur = conn.cursor()

# Teste 1: sem JOIN VMQ_CADDRE - só conta registros
t0 = time.time()
cur.execute("""
    SELECT COUNT(*) FROM VMQ_DREQLIK d
    WHERE d.DTREF >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND d.DTREF <  TO_DATE('2026-10-01','YYYY-MM-DD')
""")
r = cur.fetchone()
print(f'COUNT sem JOIN: {r[0]} linhas em {time.time()-t0:.1f}s')

# Teste 2: VMQ_CADDRE sozinha
t0 = time.time()
cur.execute("SELECT COUNT(*) FROM VMQ_CADDRE")
r = cur.fetchone()
print(f'VMQ_CADDRE: {r[0]} linhas em {time.time()-t0:.1f}s')

# Teste 3: JOIN simples
t0 = time.time()
cur.execute("""
    SELECT COUNT(*) FROM VMQ_DREQLIK d
    JOIN VMQ_CADDRE c ON c.CODNAT=d.CODNAT AND c.CODCENCUS=d.CODCENCUS AND c.REF=d.REF
    WHERE d.DTREF >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND d.DTREF <  TO_DATE('2026-10-01','YYYY-MM-DD')
""")
r = cur.fetchone()
print(f'COUNT com JOIN: {r[0]} linhas em {time.time()-t0:.1f}s')

cur.close()
conn.close()
