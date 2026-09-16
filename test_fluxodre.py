import oracledb, time

conn = oracledb.connect(user='sankhya', password='mqh41r', dsn='192.168.1.55/ORCL')
cur = conn.cursor()

# Verifica se existe tabela AD_FLUXODRE (dados pré-calculados usados pela view)
t0 = time.time()
cur.execute("""
    SELECT DTNEG, CODEMP, CODCENCUS, CODNAT, TIPOITEM, VALOR
    FROM AD_FLUXODRE
    WHERE ROWNUM <= 3
""")
rows = cur.fetchall()
cols = [c[0] for c in cur.description]
print(f'AD_FLUXODRE cols: {cols}')
for r in rows: print(r)
print(f'Tempo: {time.time()-t0:.1f}s')

# Conta registros de setembro 2026
t0 = time.time()
cur.execute("""
    SELECT COUNT(*) FROM AD_FLUXODRE
    WHERE DTNEG >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND DTNEG <  TO_DATE('2026-10-01','YYYY-MM-DD')
""")
print(f'Registros set/2026: {cur.fetchone()[0]} em {time.time()-t0:.1f}s')

cur.close()
conn.close()
