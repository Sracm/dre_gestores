import json
import sqlite3

with open('scratch/pbi_parceiros_audit.json', 'r', encoding='utf-8-sig') as f:
    pbi_rows = json.load(f)

conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()

diffs = []
print(f"Total PBI Partner rows: {len(pbi_rows)}")
print("=" * 125)
header = f"{'MES':<4} | {'NATUREZA':<32} | {'PARCEIRO':<38} | {'ORC PBI':>10} | {'ORC DB':>10} | {'REAL PBI':>10} | {'REAL DB':>10} | STATUS"
print(header)
print("-" * 125)

for r in pbi_rows:
    mes = r['mes']
    nat = r['descrnat'].strip()
    parc = r['parceiro'].strip()
    orc_pbi = round(float(r['orcado'] or 0.0), 2)
    real_pbi = round(float(r['realizado'] or 0.0), 2)
    
    cur.execute("""
        SELECT SUM(orcado), SUM(realizado)
        FROM dre_detalhe_rh
        WHERE ano = 2026 AND mes = ? AND descrnat = ? AND parceiro = ?
    """, (mes, nat, parc))
    db_res = cur.fetchone()
    orc_db = round(float(db_res[0] or 0.0), 2)
    real_db = round(float(db_res[1] or 0.0), 2)
    
    diff_orc = abs(orc_pbi - orc_db)
    diff_real = abs(real_pbi - real_db)
    
    if diff_orc < 0.01 and diff_real < 0.01:
        status = "OK (100% EXATO)"
    else:
        status = "DIVERGENCIA"
        diffs.append((mes, nat, parc, orc_pbi, orc_db, real_pbi, real_db))
        
    line = f"{mes:<4} | {nat:<32.32} | {parc:<38.38} | {orc_pbi:>10.2f} | {orc_db:>10.2f} | {real_pbi:>10.2f} | {real_db:>10.2f} | {status}"
    print(line)

print("=" * 125)
print(f"RESULTADO FINAL: {len(pbi_rows)} LINHAS AUDITADAS | TOTAL DE DIVERGENCIAS: {len(diffs)}")
