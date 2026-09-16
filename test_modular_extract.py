import oracledb, time
from collections import defaultdict

print("Iniciando extração modular direta do Oracle para Setembro/2026...")
t_inicio = time.time()

conn = oracledb.connect(user="sankhya", password="mqh41r", dsn="192.168.1.55/ORCL")
cur = conn.cursor()

# 1. Carrega VMQ_CADDRE em memória (33k linhas - ultra rápido)
print("1. Carregando VMQ_CADDRE...")
t0 = time.time()
cur.execute("""
    SELECT CODCENCUS, CODNAT, REF, BLOCO, TITULO, NVL(FATOR, 1) AS FATOR
    FROM VMQ_CADDRE
""")
caddre_map = {}
for r in cur.fetchall():
    # chave: (codcencus, codnat, ref)
    caddre_map[(r[0], r[1], r[2])] = {"bloco": r[3], "titulo": r[4], "fator": float(r[5])}
print(f"   VMQ_CADDRE carregada: {len(caddre_map)} regras em {time.time()-t0:.2f}s")

# 2. Carrega COM de set/2026
print("2. Consultando COM...")
t0 = time.time()
cur.execute("""
    SELECT
        CAB.CODEMP,
        COALESCE(CAB.CODCENCUS,0) AS CODCENCUS,
        CAB.CODNAT AS CODNAT,
        SUM(((ITE.VLRTOT - ITE.VLRDESC - ITE.VLRREPRED + ITE.VLRSUBST + ITE.VLRIPI) * VCA.INDITENSBRUTO)) AS VALORNF,
        SUM(CASE WHEN CAB.CODTIPOPER IN (4092,3320,4091) THEN (ITE.AD_CUSTO_OPER_CHINA* ITE.QTDNEG)*CAB.VLRMOEDA ELSE
            COALESCE(CASE WHEN (CAB.CODEMP <> 501 OR TOP.CODTIPOPER=3291) THEN (F_OBTEM_CUSTO_MQ ((CASE WHEN TOP.CODTIPOPER=3291 THEN 2 ELSE CAB.CODEMP END), ITE.CODPROD, CAB.DTNEG, CAB.DTNEG) * ITE.QTDNEG) END * (CASE WHEN CAB.CODTIPOPER=11000 THEN 0 ELSE 1 END), 0)
        END) AS CUSTOGER,
        SUM(CASE WHEN CAB.CODEMP <> 501 THEN (OBTEMCUSTO(ITE.CODPROD,'S',CAB.CODEMP,'N',0,'N',0,CAB.DTENTSAI,3) * ITE.QTDNEG) END * (CASE WHEN CAB.CODTIPOPER=11000 THEN 0 ELSE 1 END)) AS CUSSIMICM,
        SUM(F_OBTEM_IMPOSTOSITE(CAB.NUNOTA, ITE.SEQUENCIA)) AS IMPOSTO
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
    GROUP BY CAB.CODEMP, CAB.CODCENCUS, CAB.CODNAT
""")
com_rows = cur.fetchall()
print(f"   COM retornou {len(com_rows)} grupos em {time.time()-t0:.2f}s")

# 3. Carrega FIN de set/2026
print("3. Consultando FIN...")
t0 = time.time()
cur.execute("""
    SELECT 
        FIN.CODEMP,
        FIN.CODCENCUS,
        FIN.CODNAT,
        SUM(FIN.VLRDESDOB * FIN.RECDESP) AS VALORFIN
    FROM VGFFINRAT FIN 
    WHERE FIN.RECDESP IN (1,-1)
      AND FIN.PROVISAO = 'N'
      AND (
          (FIN.CODNAT NOT IN (2010101,2010116,2010120,12010201,12010401,12020408) 
           AND FIN.DTNEG >= TO_DATE('2026-09-01','YYYY-MM-DD') AND FIN.DTNEG < TO_DATE('2026-10-01','YYYY-MM-DD'))
          OR
          (FIN.CODNAT IN (2010101,2010116,2010120,12010201,12010401,12020408)
           AND FIN.DTNEG >= TO_DATE('2026-10-01','YYYY-MM-DD') AND FIN.DTNEG < TO_DATE('2026-11-01','YYYY-MM-DD'))
      )
    GROUP BY FIN.CODEMP, FIN.CODCENCUS, FIN.CODNAT
""")
fin_rows = cur.fetchall()
print(f"   FIN retornou {len(fin_rows)} grupos em {time.time()-t0:.2f}s")

# 4. Carrega FINACRESDESC de set/2026
print("4. Consultando FINACRESDESC...")
t0 = time.time()
cur.execute("""
    SELECT 
        FIN.CODEMP,
        FIN.CODCENCUS,
        FIN.CODNAT,
        SUM(((FIN.VLRDESC) * FIN.RECDESP * (-1)) * CASE WHEN (FIN.VLRDESDOB>0 AND FIN.VLRATUALIZADO>0) THEN (FIN.VLRDESDOB/FIN.VLRATUALIZADO) ELSE 1 END) AS CARTAODESC,
        SUM(((FIN.VLRMULTA+FIN.VLRJURO) * FIN.RECDESP) * CASE WHEN (FIN.VLRDESDOB>0 AND FIN.VLRATUALIZADO>0) THEN (FIN.VLRDESDOB/FIN.VLRATUALIZADO) ELSE 1 END) AS FINACRESC,
        SUM(((FIN.CARTAODESC) * FIN.RECDESP * (-1)) * CASE WHEN (FIN.VLRDESDOB>0 AND FIN.VLRATUALIZADO>0) THEN (FIN.VLRDESDOB/FIN.VLRATUALIZADO) ELSE 1 END) AS TAXAADM,
        SUM((FIN.VLRVARCAMBIAL * FIN.RECDESP)) AS VARCAMBIAL
    FROM VGFFINRAT FIN 
    WHERE FIN.RECDESP IN (1,-1)
      AND FIN.PROVISAO = 'N'
      AND FIN.CODCENCUS NOT IN (20010000, 21010000)
      AND (
          (FIN.CODNAT NOT IN (2010101,2010116,2010120,12010201,12010401,12020408) 
           AND FIN.DHBAIXA >= TO_DATE('2026-09-01','YYYY-MM-DD') AND FIN.DHBAIXA < TO_DATE('2026-10-01','YYYY-MM-DD'))
          OR
          (FIN.CODNAT IN (2010101,2010116,2010120,12010201,12010401,12020408) 
           AND FIN.DHBAIXA >= TO_DATE('2026-10-01','YYYY-MM-DD') AND FIN.DHBAIXA < TO_DATE('2026-11-01','YYYY-MM-DD'))
      )
    GROUP BY FIN.CODEMP, FIN.CODCENCUS, FIN.CODNAT
""")
fin_acres_rows = cur.fetchall()
print(f"   FINACRESDESC retornou {len(fin_acres_rows)} grupos em {time.time()-t0:.2f}s")

# 5. Carrega INC de set/2026
print("5. Consultando INC...")
t0 = time.time()
cur.execute("""
    SELECT CODEMP, CODCENCUS, CODNAT, SUM(CASE WHEN TIPOITEM <> 'ORC' THEN VALOR ELSE 0 END) AS VALOR
    FROM AD_FLUXODRE
    WHERE DTNEG >= TO_DATE('2026-09-01','YYYY-MM-DD') AND DTNEG < TO_DATE('2026-10-01','YYYY-MM-DD')
    GROUP BY CODEMP, CODCENCUS, CODNAT
""")
inc_rows = cur.fetchall()
print(f"   INC retornou {len(inc_rows)} grupos em {time.time()-t0:.2f}s")

# 6. Carrega ORÇAMENTO de set/2026
print("6. Consultando ORCAMENTO...")
t0 = time.time()
cur.execute("""
    SELECT 501 AS CODEMP, CODCENCUS, CODNAT, REF, SUM(VLRORC) AS ORCAMENTO
    FROM AD_ORCAMENTO
    WHERE DTREF >= TO_DATE('2026-09-01','YYYY-MM-DD') AND DTREF < TO_DATE('2026-10-01','YYYY-MM-DD')
      AND CODCENCUS NOT IN (21010000)
    GROUP BY CODCENCUS, CODNAT, REF
""")
orc_rows = cur.fetchall()
print(f"   ORCAMENTO retornou {len(orc_rows)} grupos em {time.time()-t0:.2f}s")

cur.close()
conn.close()

# ── Consolidação em memória ──────────────────────────────────────────────
dre_bloco = defaultdict(lambda: {"realizado": 0.0, "orcado": 0.0})

def processar_item(codcencus, codnat, ref, valor=0.0, orcado=0.0):
    chave_ref = ref
    if codnat in (12010301, 12010302) and ref == "VALORNF":
        chave_ref = "CUSTOGER"
    
    regra = caddre_map.get((codcencus, codnat, chave_ref))
    if regra:
        fator = regra["fator"]
        bloco = regra["bloco"]
        titulo = regra["titulo"]
        dre_bloco[(bloco, titulo)]["realizado"] += float(valor or 0) * fator
        dre_bloco[(bloco, titulo)]["orcado"]    += float(orcado or 0) * fator

for r in com_rows:
    codemp, cc, nat, v_nf, c_ger, c_sim, imp = r
    if v_nf:  processar_item(cc, nat, "VALORNF", valor=v_nf)
    if c_ger: processar_item(cc, nat, "CUSTOGER", valor=c_ger)
    if c_sim: processar_item(cc, nat, "CUSSIMICM", valor=c_sim)
    if imp:   processar_item(cc, nat, "IMPOSTO", valor=imp)

for r in fin_rows:
    codemp, cc, nat, v_fin = r
    if v_fin: processar_item(cc, nat, "VALORFIN", valor=v_fin)

for r in fin_acres_rows:
    codemp, cc, nat, card, acres, taxa, varcamb = r
    if card:   processar_item(cc, nat, "CARTAODESC", valor=card)
    if acres:  processar_item(cc, nat, "FINACRESC", valor=acres)
    if taxa:   processar_item(cc, nat, "TAXAADM", valor=taxa)
    if varcamb: processar_item(cc, nat, "VARCAMBIAL", valor=varcamb)

for r in inc_rows:
    codemp, cc, nat, v_inc = r
    if v_inc: processar_item(cc, nat, "INCQLIK", valor=v_inc)

for r in orc_rows:
    codemp, cc, nat, ref, v_orc = r
    if v_orc: processar_item(cc, nat, ref, orcado=v_orc)

print(f"\n=======================================================")
print(f"RESULTADO DRE SET/2026 EXTRAÍDO DIRETO DO ORACLE EM {time.time()-t_inicio:.2f}s:")
print(f"=======================================================")
for (bloco, titulo), vals in sorted(dre_bloco.items()):
    print(f"{bloco} -> {titulo}: Realizado = {vals['realizado']:,.2f} | Orçado = {vals['orcado']:,.2f}")
