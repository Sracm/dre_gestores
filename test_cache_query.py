import sqlite3
import time

conn = sqlite3.connect("dre_cache.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Teste 1: Filtros ---")
t0 = time.time()
cur.execute("SELECT ano FROM dre_filtros_anos")
anos = [r["ano"] for r in cur.fetchall()]
cur.execute("SELECT nome FROM dre_filtros_empresas")
empresas = [r["nome"] for r in cur.fetchall()]
cur.execute("SELECT codcencus, nome FROM dre_filtros_centros")
centros = [r["nome"] for r in cur.fetchall()]
print(f"Filtros lidos em {time.time()-t0:.4f}s: {len(anos)} anos, {len(empresas)} empresas, {len(centros)} centros")
print(f"Anos: {anos}")
print(f"Empresas: {empresas}")

print("\n--- Teste 2: DRE Principal para 2026-08 (Todas empresas e centros) ---")
t0 = time.time()
cur.execute("""
    SELECT
        bloco,
        titulo,
        descrnat,
        SUM(realizado) AS realizado,
        SUM(orcado) AS orcado
    FROM dre_data
    WHERE ano = 2026 AND mes = 8
    GROUP BY bloco, titulo, descrnat
    ORDER BY bloco, titulo, descrnat
""")
rows = cur.fetchall()
print(f"DRE Principal lido em {time.time()-t0:.4f}s: {len(rows)} linhas detalhadas")

# Totais por bloco
blocos = {}
for r in rows:
    b = r["bloco"]
    if b not in blocos:
        blocos[b] = {"real": 0.0, "orc": 0.0}
    blocos[b]["real"] += r["realizado"] or 0.0
    blocos[b]["orc"] += r["orcado"] or 0.0

print("\nTotais por Bloco:")
for b, val in sorted(blocos.items()):
    print(f"  {b:<40} Real: R$ {val['real']:>12,.2f} | Orc: R$ {val['orc']:>12,.2f}")

print("\n--- Teste 3: Evolução Mensal 2026 ---")
t0 = time.time()
cur.execute("""
    SELECT mes, bloco, SUM(realizado) as realizado, SUM(orcado) as orcado
    FROM dre_resumo_mensal
    WHERE ano = 2026
    GROUP BY mes, bloco
    ORDER BY mes, bloco
""")
mensal = cur.fetchall()
print(f"Evolução mensal lida em {time.time()-t0:.4f}s: {len(mensal)} registros")

print("\n--- Teste 4: Por Empresa 2026-08 ---")
t0 = time.time()
cur.execute("""
    SELECT empresa, bloco, SUM(realizado) as realizado, SUM(orcado) as orcado
    FROM dre_data
    WHERE ano = 2026 AND mes = 8 AND empresa IS NOT NULL AND empresa != ''
    GROUP BY empresa, bloco
    ORDER BY empresa, bloco
""")
por_emp = cur.fetchall()
print(f"Por empresa lido em {time.time()-t0:.4f}s: {len(por_emp)} registros")

conn.close()
