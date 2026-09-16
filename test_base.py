import oracledb, time

conn = oracledb.connect(user='sankhya', password='mqh41r', dsn='192.168.1.55/ORCL')
cur = conn.cursor()

# Teste: filtra por BASE para identificar qual union é lento
for base in ['COM', 'FIN', 'FINACRESDESC', 'INC']:
    t0 = time.time()
    cur.execute("""
        SELECT c.BLOCO, c.TITULO,
               SUM(d.VALOR * NVL(c.FATOR,1)) AS REALIZADO,
               SUM(d.ORCAMENTO * NVL(c.FATOR,1)) AS ORCADO
        FROM VMQ_DREQLIK d
        JOIN VMQ_CADDRE c ON c.CODNAT=d.CODNAT
                          AND c.CODCENCUS=d.CODCENCUS
                          AND c.REF=d.REF
        WHERE d.BASE = :base
          AND d.DTREF >= TO_DATE('2026-09-01','YYYY-MM-DD')
          AND d.DTREF <  TO_DATE('2026-10-01','YYYY-MM-DD')
        GROUP BY c.BLOCO, c.TITULO
        ORDER BY c.BLOCO, c.TITULO
    """, base=base)
    rows = cur.fetchall()
    print(f'BASE={base}: {len(rows)} grupos em {time.time()-t0:.1f}s')
    for r in rows:
        print(f'  {r}')

cur.close()
conn.close()
