import sqlite3
from collections import OrderedDict
import json

ALLOWED_COMPANIES = [
    'Consolidação', 'FORX', 'MCR - FABRICA', 'MCR - FILIAL 03', 
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ', 
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]

conn = sqlite3.connect("dre_cache.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

companies_ph = ",".join(["?"] * len(ALLOWED_COMPANIES))
sql = f"""
    SELECT
        bloco,
        titulo,
        descrnat,
        SUM(realizado) AS realizado,
        SUM(orcado) AS orcado
    FROM dre_data
    WHERE ano = 2026 AND mes = 3
      AND empresa IN ({companies_ph})
      AND codcencus != 21010000
    GROUP BY bloco, titulo, descrnat
    ORDER BY bloco, titulo, descrnat
"""
cur.execute(sql, ALLOWED_COMPANIES)
rows = [dict(r) for r in cur.fetchall()]

blocos_dict = OrderedDict()

for r in rows:
    bloco  = r.get("bloco")  or ""
    titulo = r.get("titulo") or ""
    descr  = r.get("descrnat") or ""
    real   = float(r.get("realizado") or 0)
    orc    = float(r.get("orcado") or 0)

    if bloco not in blocos_dict:
        blocos_dict[bloco] = {
            "bloco": bloco,
            "realizado": 0.0,
            "orcado": 0.0,
            "titulos": OrderedDict()
        }

    if titulo not in blocos_dict[bloco]["titulos"]:
        blocos_dict[bloco]["titulos"][titulo] = {
            "titulo": titulo,
            "realizado": 0.0,
            "orcado": 0.0,
            "linhas": []
        }

    blocos_dict[bloco]["titulos"][titulo]["linhas"].append({
        "descr": descr,
        "realizado": real,
        "orcado": orc
    })
    blocos_dict[bloco]["titulos"][titulo]["realizado"] += real
    blocos_dict[bloco]["titulos"][titulo]["orcado"]    += orc
    blocos_dict[bloco]["realizado"] += real
    blocos_dict[bloco]["orcado"]    += orc

# Base para cálculo de % sobre Venda Bruta
vb_real = 0.0
vb_orc = 0.0
for b, bd in blocos_dict.items():
    for t, td in bd["titulos"].items():
        if "venda bruta" in t.lower():
            vb_real = td["realizado"]
            vb_orc = td["orcado"]
            break
    if vb_real:
        break

if not vb_real:
    vb_real = 1.0
if not vb_orc:
    vb_orc = 1.0

margem_real = sum(bd["realizado"] for bd in blocos_dict.values())
margem_orc  = sum(bd["orcado"]    for bd in blocos_dict.values())

def pct(n, d):
    return round((n / d) * 100, 1) if d else None

def ro(r, o):
    if not o or abs(o) < 0.001:
        return None
    return round(((r - o) / abs(o)) * 100, 1)

print(f"VB Real: {vb_real:,.2f} | VB Orc: {vb_orc:,.2f}")
print(f"Margem Real: {margem_real:,.2f} ({pct(margem_real, vb_real)}%) | Margem Orc: {margem_orc:,.2f} ({pct(margem_orc, vb_orc)}%) | R/O: {ro(margem_real, margem_orc)}%")

print("\n" + "="*85)
print(f"{'DESCRIÇÃO':<35} | {'ORÇADO (R$)':>14} | {'REALIZADO (R$)':>14} | {'% VB ORÇ':>9} | {'% VB REAL':>10} | {'R/O':>7}")
print("="*85)

print(f"{'Margem de Contribuição':<35} | {margem_orc:>14,.0f} | {margem_real:>14,.0f} | {str(pct(margem_orc, vb_orc))+'%':>9} | {str(pct(margem_real, vb_real))+'%':>10} | {str(ro(margem_real, margem_orc))+'%':>7}")

for bloco, bd in blocos_dict.items():
    p_orc = f"{pct(bd['orcado'], vb_orc)}%" if pct(bd['orcado'], vb_orc) is not None else "-"
    p_real = f"{pct(bd['realizado'], vb_real)}%" if pct(bd['realizado'], vb_real) is not None else "-"
    r_o = f"{ro(bd['realizado'], bd['orcado'])}%" if ro(bd['realizado'], bd['orcado']) is not None else "-"
    print(f"\n{bloco:<35} | {bd['orcado']:>14,.0f} | {bd['realizado']:>14,.0f} | {p_orc:>9} | {p_real:>10} | {r_o:>7}")
    
    for titulo, td in bd["titulos"].items():
        tp_orc = f"{pct(td['orcado'], vb_orc)}%" if pct(td['orcado'], vb_orc) is not None else "-"
        tp_real = f"{pct(td['realizado'], vb_real)}%" if pct(td['realizado'], vb_real) is not None else "-"
        tr_o = f"{ro(td['realizado'], td['orcado'])}%" if ro(td['realizado'], td['orcado']) is not None else "-"
        print(f"  {titulo:<33} | {td['orcado']:>14,.0f} | {td['realizado']:>14,.0f} | {tp_orc:>9} | {tp_real:>10} | {tr_o:>7}")

conn.close()
