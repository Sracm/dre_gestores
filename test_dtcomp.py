import oracledb, time

conn = oracledb.connect(user='sankhya', password='mqh41r', dsn='192.168.1.55/ORCL')
cur = conn.cursor()
t0 = time.time()

# Testa com DTCOMP (pode ter índice melhor que DTREF)
sql = """
    SELECT c.BLOCO, c.TITULO,
           SUM(d.VALOR * NVL(c.FATOR,1)) AS REALIZADO,
           SUM(d.ORCAMENTO * NVL(c.FATOR,1)) AS ORCADO
    FROM VMQ_DREQLIK d
    JOIN VMQ_CADDRE c ON c.CODNAT=d.CODNAT AND c.CODCENCUS=d.CODCENCUS AND c.REF=d.REF
    WHERE d.DTCOMP >= TO_DATE(:1,'YYYY-MM-DD')
      AND d.DTCOMP <  TO_DATE(:2,'YYYY-MM-DD')
    GROUP BY c.BLOCO, c.TITULO
    ORDER BY c.BLOCO, c.TITULO
"""
cur.execute(sql, ['2026-09-01', '2026-10-01'])
rows = cur.fetchall()
print(f'DTCOMP OK em {time.time()-t0:.1f}s: {len(rows)} linhas')
for r in rows:
    print(r)

cur.close()
conn.close()
