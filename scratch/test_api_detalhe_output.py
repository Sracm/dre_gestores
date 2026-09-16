import sqlite3
import json
from collections import OrderedDict

def build_detalhe_response(ano=2026, meses_param="9", busca=""):
    conn = sqlite3.connect('dre_cache.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 1. Anos disponíveis
    cur.execute("SELECT DISTINCT ano FROM dre_detalhe_rh ORDER BY ano")
    anos_disp = [r[0] for r in cur.fetchall()]
    if not anos_disp:
        anos_disp = [2023, 2024, 2025, 2026]

    # 2. Meses selecionados
    month_names = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
        5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
        9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    short_names = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    if not meses_param or meses_param == "ALL":
        meses_ativos = list(range(1, 13))
    else:
        meses_ativos = []
        for p in str(meses_param).split(","):
            p = p.strip()
            if p and p.isdigit():
                m = int(p)
                if 1 <= m <= 12:
                    meses_ativos.append(m)
        if not meses_ativos:
            meses_ativos = [8]
            
    meses_info = [{"mes": m, "nome": month_names.get(m, f"Mês {m}"), "abrev": short_names.get(m, f"M{m}")} for m in sorted(meses_ativos)]

    # 3. Gráficos Trimestral e Mensal
    cur.execute("""
        SELECT tri_ano, SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
        GROUP BY tri_ano
        ORDER BY tri_ano
    """, (ano,))
    quarterly = []
    for r in cur.fetchall():
        lbl = (r["tri_ano"] or "").split("-")[0]
        quarterly.append({
            "trimestre": lbl or r["tri_ano"],
            "orcado": round(float(r["orcado"] or 0), 2),
            "realizado": round(float(r["realizado"] or 0), 2)
        })

    cur.execute("""
        SELECT mes, nomemes, SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
        GROUP BY mes, nomemes
        ORDER BY mes
    """, (ano,))
    monthly_map = {r["mes"]: r for r in cur.fetchall()}
    monthly = []
    for m in range(1, 13):
        if m in monthly_map:
            mr = monthly_map[m]
            monthly.append({
                "mes": m,
                "nomemes": short_names.get(m, mr["nomemes"]),
                "orcado": round(float(mr["orcado"] or 0), 2),
                "realizado": round(float(mr["realizado"] or 0), 2)
            })
        else:
            monthly.append({
                "mes": m,
                "nomemes": short_names.get(m, f"M{m}"),
                "orcado": 0.0,
                "realizado": 0.0
            })

    # 4. Matriz Hierárquica
    query = """
        SELECT bloco, titulo, descrnat, parceiro, mes,
               SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
    """
    params = [ano]
    if meses_ativos and len(meses_ativos) < 12:
        placeholders = ",".join("?" for _ in meses_ativos)
        query += f" AND mes IN ({placeholders})"
        params.extend(meses_ativos)

    if busca:
        query += " AND (LOWER(bloco) LIKE ? OR LOWER(titulo) LIKE ? OR LOWER(descrnat) LIKE ? OR LOWER(parceiro) LIKE ?)"
        params.extend([f"%{busca.lower()}%"] * 4)

    query += " GROUP BY bloco, titulo, descrnat, parceiro, mes ORDER BY bloco, titulo, descrnat, parceiro, mes"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    # Construção dos nós
    root = {
        "id": "root_margem",
        "nome": "Margem de Contribuição",
        "level": 0,
        "meses": {m: {"orcado": 0.0, "realizado": 0.0} for m in meses_ativos},
        "total_orcado": 0.0,
        "total_realizado": 0.0,
        "filhos": OrderedDict()
    }
    
    margem_node = {
        "id": "node_margem",
        "nome": "MARGEM",
        "level": 1,
        "meses": {m: {"orcado": 0.0, "realizado": 0.0} for m in meses_ativos},
        "total_orcado": 0.0,
        "total_realizado": 0.0,
        "filhos": OrderedDict()
    }
    root["filhos"]["MARGEM"] = margem_node

    for r in rows:
        bloco = (r["bloco"] or "Outros").strip()
        titulo = (r["titulo"] or "Outros").strip()
        descrnat = (r["descrnat"] or "Sem Natureza").strip()
        parceiro = (r["parceiro"] or "<SEM PARCEIRO>").strip()
        m = int(r["mes"]) if r["mes"] else 0
        orc = float(r["orcado"] or 0.0)
        real = float(r["realizado"] or 0.0)

        # 2. Bloco
        if bloco not in margem_node["filhos"]:
            margem_node["filhos"][bloco] = {
                "id": f"b_{len(margem_node['filhos'])}",
                "nome": bloco,
                "level": 2,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses_ativos},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        b_node = margem_node["filhos"][bloco]

        # 3. Título
        if titulo not in b_node["filhos"]:
            b_node["filhos"][titulo] = {
                "id": f"t_{b_node['id']}_{len(b_node['filhos'])}",
                "nome": titulo,
                "level": 3,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses_ativos},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        t_node = b_node["filhos"][titulo]

        # 4. Natureza
        if descrnat not in t_node["filhos"]:
            t_node["filhos"][descrnat] = {
                "id": f"n_{t_node['id']}_{len(t_node['filhos'])}",
                "nome": descrnat,
                "level": 4,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses_ativos},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        n_node = t_node["filhos"][descrnat]

        # 5. Parceiro
        if parceiro not in n_node["filhos"]:
            n_node["filhos"][parceiro] = {
                "id": f"p_{n_node['id']}_{len(n_node['filhos'])}",
                "nome": parceiro,
                "level": 5,
                "is_leaf": True,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses_ativos},
                "total_orcado": 0.0, "total_realizado": 0.0
            }
        p_node = n_node["filhos"][parceiro]

        if m in meses_ativos:
            for node in [p_node, n_node, t_node, b_node, margem_node, root]:
                node["meses"][m]["orcado"] += orc
                node["meses"][m]["realizado"] += real
                node["total_orcado"] += orc
                node["total_realizado"] += real

    # Serializa recursivamente para listas ordenadas
    def serialize_tree(node):
        out = {
            "id": node["id"],
            "nome": node["nome"],
            "level": node["level"],
            "meses": {str(k): {"orcado": round(v["orcado"], 2), "realizado": round(v["realizado"], 2)} for k, v in node["meses"].items()},
            "total_orcado": round(node["total_orcado"], 2),
            "total_realizado": round(node["total_realizado"], 2),
            "dif": round(node["total_realizado"] - node["total_orcado"], 2),
            "is_leaf": node.get("is_leaf", False)
        }
        if "filhos" in node:
            child_list = list(node["filhos"].values())
            if node["level"] == 4:
                # Parceiros: ordenar pelo maior em módulo
                child_list.sort(key=lambda x: abs(x["total_realizado"] or x["total_orcado"]), reverse=True)
            out["filhos"] = [serialize_tree(c) for c in child_list]
        return out

    serialized_root = serialize_tree(root)

    return {
        "status": "success",
        "ano": ano,
        "anos_disponiveis": anos_disp,
        "meses_selecionados": meses_info,
        "quarterly": quarterly,
        "monthly": monthly,
        "tree": [serialized_root]
    }

if __name__ == "__main__":
    res = build_detalhe_response(2026, "9")
    print("STATUS:", res["status"])
    print("MESES SELECIONADOS:", res["meses_selecionados"])
    print("ROOT:", res["tree"][0]["nome"], "TOTAL ORÇ:", res["tree"][0]["total_orcado"], "TOTAL REAL:", res["tree"][0]["total_realizado"])
    margem = res["tree"][0]["filhos"][0]
    print("MARGEM:", margem["nome"], "TOTAL ORÇ:", margem["total_orcado"], "TOTAL REAL:", margem["total_realizado"])
    for bloco in margem["filhos"]:
        print("  BLOCO:", bloco["nome"], "TOTAL REAL:", bloco["total_realizado"])
        for tit in bloco["filhos"]:
            print("    TITULO:", tit["nome"], "TOTAL REAL:", tit["total_realizado"])
            for nat in tit["filhos"]:
                if "MEDICINA" in nat["nome"]:
                    print("      NATUREZA:", nat["nome"], "TOTAL REAL:", nat["total_realizado"])
                    for parc in nat["filhos"]:
                        print("        PARCEIRO:", parc["nome"], "REAL:", parc["total_realizado"])
