import oracledb, time

conn = oracledb.connect(user="sankhya", password="mqh41r", dsn="192.168.1.55/ORCL")
cur = conn.cursor()

print("--- Teste 1: Subquery COM filtrada por DTENTSAI em set/2026 ---")
t0 = time.time()
cur.execute("""
    SELECT COUNT(*)
    FROM TGFCAB CAB, TGFITE ITE, TGFTOP TOP, VGFCAB VCA
    WHERE CAB.CODTIPOPER = TOP.CODTIPOPER
      AND CAB.DHTIPOPER = TOP.DHALTER
      AND CAB.NUNOTA = ITE.NUNOTA
      AND CAB.TIPMOV IN ('V', 'D')
      AND CAB.STATUSNOTA = 'L' 
      AND CAB.NUNOTA = VCA.NUNOTA
      AND (TOP.GOLSINAL = -1 OR BONIFICACAO='S' OR CAB.CODTIPOPER IN (3218,3327))
      AND (NOT EXISTS(SELECT 1 FROM TGFVAR VAR WHERE VAR.NUNOTA = ITE.NUNOTA AND VAR.NUNOTAORIG = VAR.NUNOTA AND VAR.SEQUENCIAORIG = ITE.SEQUENCIA))
      AND (TOP.ATUALFINTERC <> 'N' OR TOP.ATUALESTTERC = 'N' OR ITE.TERCEIROS <> 'S')
      AND ITE.SEQUENCIA > 0    
      AND TOP.GOLDEV IN (1,-1) 
      AND CAB.DTENTSAI >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND CAB.DTENTSAI <  TO_DATE('2026-10-01','YYYY-MM-DD')
""")
print(f"COM count: {cur.fetchone()[0]} em {time.time()-t0:.2f}s")

print("\n--- Teste 2: Subquery FIN filtrada por DTNEG em set/2026 ---")
t0 = time.time()
cur.execute("""
    SELECT COUNT(*)
    FROM VGFFINRAT FIN 
    WHERE FIN.recdesp IN (1,-1)
      AND FIN.provisao='N'
      AND fin.dtneg >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND fin.dtneg <  TO_DATE('2026-10-01','YYYY-MM-DD')
""")
print(f"FIN count: {cur.fetchone()[0]} em {time.time()-t0:.2f}s")

print("\n--- Teste 3: Subquery FINACRESDESC filtrada por DHBAIXA em set/2026 ---")
t0 = time.time()
cur.execute("""
    SELECT COUNT(*)
    FROM VGFFINRAT FIN 
    WHERE FIN.recdesp IN (1,-1)
      AND FIN.provisao='N'
      AND FIN.DHBAIXA >= TO_DATE('2026-09-01','YYYY-MM-DD')
      AND FIN.DHBAIXA <  TO_DATE('2026-10-01','YYYY-MM-DD')
      AND fin.codcencus NOT IN (20010000, 21010000)
""")
print(f"FINACRESDESC count: {cur.fetchone()[0]} em {time.time()-t0:.2f}s")

cur.close()
conn.close()
