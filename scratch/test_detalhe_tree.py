import sqlite3
import json

def test_detalhe_tree():
    conn = sqlite3.connect('dre_cache.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    ano = 2026
    query = """
        SELECT bloco, titulo, descrnat, parceiro, mes, SUM(orcado) as orcado, SUM(realizado) as realizado
        FROM dre_detalhe_rh
        WHERE ano = ?
        GROUP BY bloco, titulo, descrnat, parceiro, mes
        ORDER BY bloco, titulo, descrnat, parceiro, mes
    """
    cur.execute(query, (ano,))
    rows = cur.fetchall()
    
    tree = {}
    grand_total = {
        "meses": {m: {"orcado": 0.0, "realizado": 0.0} for m in range(1, 13)},
        "total_orcado": 0.0,
        "total_realizado": 0.0,
        "dif": 0.0
    }
    
    for r in rows:
        bloco = r["bloco"] or "Sem Bloco"
        titulo = r["titulo"] or "Sem Título"
        descrnat = r["descrnat"] or "Sem Natureza"
        parceiro = r["parceiro"] or "<SEM PARCEIRO>"
        m = r["mes"]
        orc = r["orcado"] or 0.0
        real = r["realizado"] or 0.0
        
        if bloco not in tree:
            tree[bloco] = {
                "nome": bloco,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in range(1, 13)},
                "total_orcado": 0.0, "total_realizado": 0.0, "dif": 0.0,
                "titulos": {}
            }
        b_node = tree[bloco]
        if titulo not in b_node["titulos"]:
            b_node["titulos"][titulo] = {
                "nome": titulo,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in range(1, 13)},
                "total_orcado": 0.0, "total_realizado": 0.0, "dif": 0.0,
                "naturezas": {}
            }
        t_node = b_node["titulos"][titulo]
        if descrnat not in t_node["naturezas"]:
            t_node["naturezas"][descrnat] = {
                "nome": descrnat,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in range(1, 13)},
                "total_orcado": 0.0, "total_realizado": 0.0, "dif": 0.0,
                "parceiros": {}
            }
        n_node = t_node["naturezas"][descrnat]
        if parceiro not in n_node["parceiros"]:
            n_node["parceiros"][parceiro] = {
                "nome": parceiro,
                "meses": {i: {"orcado": 0.0, "realizado": 0.0} for i in range(1, 13)},
                "total_orcado": 0.0, "total_realizado": 0.0, "dif": 0.0
            }
        p_node = n_node["parceiros"][parceiro]
        
        # Accumulate
        if 1 <= m <= 12:
            p_node["meses"][m]["orcado"] += orc
            p_node["meses"][m]["realizado"] += real
            p_node["total_orcado"] += orc
            p_node["total_realizado"] += real
            p_node["dif"] += (real - orc)
            
            n_node["meses"][m]["orcado"] += orc
            n_node["meses"][m]["realizado"] += real
            n_node["total_orcado"] += orc
            n_node["total_realizado"] += real
            n_node["dif"] += (real - orc)
            
            t_node["meses"][m]["orcado"] += orc
            t_node["meses"][m]["realizado"] += real
            t_node["total_orcado"] += orc
            t_node["total_realizado"] += real
            t_node["dif"] += (real - orc)
            
            b_node["meses"][m]["orcado"] += orc
            b_node["meses"][m]["realizado"] += real
            b_node["total_orcado"] += orc
            b_node["total_realizado"] += real
            b_node["dif"] += (real - orc)
            
            grand_total["meses"][m]["orcado"] += orc
            grand_total["meses"][m]["realizado"] += real
            grand_total["total_orcado"] += orc
            grand_total["total_realizado"] += real
            grand_total["dif"] += (real - orc)

    conn.close()
    
    # Convert dicts to lists for easy JSON consumption
    blocos_list = []
    for b_k, b_v in tree.items():
        titulos_list = []
        for t_k, t_v in b_v["titulos"].items():
            nats_list = []
            for n_k, n_v in t_v["naturezas"].items():
                parcs_list = list(n_v["parceiros"].values())
                parcs_list.sort(key=lambda x: abs(x["total_realizado"] or x["total_orcado"]), reverse=True)
                n_v["parceiros"] = parcs_list
                nats_list.append(n_v)
            nats_list.sort(key=lambda x: abs(x["total_realizado"] or x["total_orcado"]), reverse=True)
            t_v["naturezas"] = nats_list
            titulos_list.append(t_v)
        b_v["titulos"] = titulos_list
        blocos_list.append(b_v)
        
    print(f"Blocos: {len(blocos_list)}")
    print(f"Grand Total Orçado: {grand_total['total_orcado']:,.2f}")
    print(f"Grand Total Realizado: {grand_total['total_realizado']:,.2f}")
    print(f"Sample block: {blocos_list[0]['nome']}, titulos: {len(blocos_list[0]['titulos'])}")

test_detalhe_tree()
