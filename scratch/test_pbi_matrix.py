import sqlite3
from collections import OrderedDict

def build_pbi_matrix(ano=2026, meses=[9], busca=""):
    conn = sqlite3.connect('dre_cache.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = """
        SELECT bloco, titulo, descrnat, parceiro, mes, nomemes,
               SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
    """
    params = [ano]
    if meses and "ALL" not in meses:
        placeholders = ",".join("?" for _ in meses)
        query += f" AND mes IN ({placeholders})"
        params.extend(meses)
        
    if busca:
        query += " AND (LOWER(bloco) LIKE ? OR LOWER(titulo) LIKE ? OR LOWER(descrnat) LIKE ? OR LOWER(parceiro) LIKE ?)"
        params.extend([f"%{busca.lower()}%"] * 4)
        
    query += " GROUP BY bloco, titulo, descrnat, parceiro, mes ORDER BY bloco, titulo, descrnat, parceiro, mes"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    # We construct the hierarchy:
    # Margem de Contribuição -> MARGEM -> BLOCO -> TITULO -> DESCRNAT -> PARCEIRO
    root = {
        "id": "root_margem",
        "nome": "Margem de Contribuição",
        "meses": {m: {"orcado": 0.0, "realizado": 0.0} for m in meses},
        "total_orcado": 0.0,
        "total_realizado": 0.0,
        "filhos": OrderedDict() # MARGEM
    }
    
    margem_node = {
        "id": "node_margem",
        "nome": "MARGEM",
        "meses": {m: {"orcado": 0.0, "realizado": 0.0} for m in meses},
        "total_orcado": 0.0,
        "total_realizado": 0.0,
        "filhos": OrderedDict() # BLOCos
    }
    root["filhos"]["MARGEM"] = margem_node
    
    for r in rows:
        bloco = (r["bloco"] or "Outros").strip()
        titulo = (r["titulo"] or "Outros").strip()
        descrnat = (r["descrnat"] or "Sem Natureza").strip()
        parceiro = (r["parceiro"] or "<SEM PARCEIRO>").strip()
        m = r["mes"]
        orc = float(r["orcado"] or 0.0)
        real = float(r["realizado"] or 0.0)
        
        # 1. Bloco
        if bloco not in margem_node["filhos"]:
            margem_node["filhos"][bloco] = {
                "id": f"b_{len(margem_node['filhos'])}",
                "nome": bloco,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        b_node = margem_node["filhos"][bloco]
        
        # 2. Título
        if titulo not in b_node["filhos"]:
            b_node["filhos"][titulo] = {
                "id": f"t_{b_node['id']}_{len(b_node['filhos'])}",
                "nome": titulo,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        t_node = b_node["filhos"][titulo]
        
        # 3. Natureza
        if descrnat not in t_node["filhos"]:
            t_node["filhos"][descrnat] = {
                "id": f"n_{t_node['id']}_{len(t_node['filhos'])}",
                "nome": descrnat,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "filhos": OrderedDict()
            }
        n_node = t_node["filhos"][descrnat]
        
        # 4. Parceiro
        if parceiro not in n_node["filhos"]:
            n_node["filhos"][parceiro] = {
                "id": f"p_{n_node['id']}_{len(n_node['filhos'])}",
                "nome": parceiro,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in meses},
                "total_orcado": 0.0, "total_realizado": 0.0,
                "is_leaf": True
            }
        p_node = n_node["filhos"][parceiro]
        
        # Add values
        if m in meses:
            p_node["meses"][m]["orcado"] += orc
            p_node["meses"][m]["realizado"] += real
            p_node["total_orcado"] += orc
            p_node["total_realizado"] += real
            
            n_node["meses"][m]["orcado"] += orc
            n_node["meses"][m]["realizado"] += real
            n_node["total_orcado"] += orc
            n_node["total_realizado"] += real
            
            t_node["meses"][m]["orcado"] += orc
            t_node["meses"][m]["realizado"] += real
            t_node["total_orcado"] += orc
            t_node["total_realizado"] += real
            
            b_node["meses"][m]["orcado"] += orc
            b_node["meses"][m]["realizado"] += real
            b_node["total_orcado"] += orc
            b_node["total_realizado"] += real
            
            margem_node["meses"][m]["orcado"] += orc
            margem_node["meses"][m]["realizado"] += real
            margem_node["total_orcado"] += orc
            margem_node["total_realizado"] += real
            
            root["meses"][m]["orcado"] += orc
            root["meses"][m]["realizado"] += real
            root["total_orcado"] += orc
            root["total_realizado"] += real

    print("=== ROOT ===")
    print(f"Nome: {root['nome']} | Total Orç: {root['total_orcado']:,.2f} | Total Real: {root['total_realizado']:,.2f}")
    
    print("=== BLOCOS ===")
    for b_name, b_data in margem_node["filhos"].items():
        print(f"  Bloco: {b_name} | Orç: {b_data['total_orcado']:,.2f} | Real: {b_data['total_realizado']:,.2f}")
        for t_name, t_data in b_data["filhos"].items():
            print(f"    Título: {t_name} | Orç: {t_data['total_orcado']:,.2f} | Real: {t_data['total_realizado']:,.2f}")
            for n_name, n_data in t_data["filhos"].items():
                if "MEDICINA" in n_name or "ASSESSORIA" in n_name:
                    print(f"      Natureza: {n_name} | Orç: {n_data['total_orcado']:,.2f} | Real: {n_data['total_realizado']:,.2f}")
                    for p_name, p_data in n_data["filhos"].items():
                        print(f"        Parceiro: {p_name} | Orç: {p_data['total_orcado']:,.2f} | Real: {p_data['total_realizado']:,.2f}")

build_pbi_matrix(2026, [9])
