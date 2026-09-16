import sqlite3

conn = sqlite3.connect("dre_cache.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Totais por Empresa em Março/2026 ---")
cur.execute("""
    SELECT empresa, SUM(realizado) as real, SUM(orcado) as orc
    FROM dre_data
    WHERE ano = 2026 AND mes = 3
    GROUP BY empresa
    ORDER BY real DESC
""")
for r in cur.fetchall():
    print(f"  {r['empresa']:<25} Real: R$ {r['real']:>12,.2f} | Orc: R$ {r['orc']:>12,.2f}")

print("\n--- Totais por Bloco e Titulo em Março/2026 (Todas as empresas) ---")
cur.execute("""
    SELECT bloco, titulo, SUM(realizado) as real, SUM(orcado) as orc
    FROM dre_data
    WHERE ano = 2026 AND mes = 3
    GROUP BY bloco, titulo
    ORDER BY bloco, titulo
""")
for r in cur.fetchall():
    print(f"  {r['bloco']} -> {r['titulo']:<35} Real: R$ {r['real']:>12,.2f} | Orc: R$ {r['orc']:>12,.2f}")

conn.close()
