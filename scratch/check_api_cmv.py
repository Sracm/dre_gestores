import urllib.request
import json

for m in [1, 2, 3]:
    url = f"http://127.0.0.1:5150/api/dre?ano=2026&mes={m}&emp=ALL&cenc=ALL"
    resp = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    print(f"=== MÊS {m} ===")
    for b in resp["dre"]:
        if "Custo" in b["bloco"]:
            # R/O Ajustado
            diff_pct = ((b["realizado"] - b["orcado"]) / abs(b["orcado"]) * 100) if b["orcado"] != 0 else 0
            print(f"Bloco: {b['bloco']} | Orç: {b['orcado']:,.0f} | Real: {b['realizado']:,.0f} | % Orç: {b['perc_orcado']:.2f}% | % Real: {b['perc_realizado']:.2f}% | R/O: {diff_pct:.2f}%")
            for t in b["titulos"]:
                t_diff_pct = ((t["realizado"] - t["orcado"]) / abs(t["orcado"]) * 100) if t["orcado"] != 0 else 0
                print(f"   Título: {t['titulo']} | Orç: {t['orcado']:,.0f} | Real: {t['realizado']:,.0f} | % Orç: {t['perc_orcado']:.2f}% | % Real: {t['perc_realizado']:.2f}% | R/O: {t_diff_pct:.2f}%")
