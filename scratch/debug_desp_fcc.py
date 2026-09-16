import sqlite3

conn = sqlite3.connect('dre_cache.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Ver todos os registros de DESP FCC COMERCIAL na tabela dre_detalhe_fsp
cur.execute("""
    SELECT codcencus, ano, mes, bloco, titulo, descrnat, parceiro, orcado, realizado
    FROM dre_detalhe_fsp
    WHERE descrnat LIKE '%DESP FCC COMERCIAL%'
      AND ano = 2026
    ORDER BY codcencus, mes
""")
rows = cur.fetchall()
print(f"=== dre_detalhe_fsp: DESP FCC COMERCIAL ===")
print(f"Total linhas: {len(rows)}")
for r in rows:
    print(f"  codcencus={r['codcencus']} | mes={r['mes']} | orcado={r['orcado']} | realizado={r['realizado']} | parceiro={r['parceiro']}")

print()

# Verificar no dre_data (tabela geral) - o CENCUS que tem realizado para esse lançamento
cur.execute("""
    SELECT codcencus, descrcencus, ano, mes, titulo, descrnat, realizado, orcado
    FROM dre_data
    WHERE descrnat LIKE '%DESP FCC COMERCIAL%'
      AND ano = 2026
    ORDER BY codcencus, mes
""")
rows2 = cur.fetchall()
print(f"=== dre_data: DESP FCC COMERCIAL ===")
print(f"Total linhas: {len(rows2)}")
for r in rows2:
    print(f"  codcencus={r['codcencus']} descrcencus={r['descrcencus']} | mes={r['mes']} | orcado={r['orcado']} | realizado={r['realizado']}")

conn.close()
