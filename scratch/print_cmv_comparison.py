import urllib.request
import json

for m in [1, 2, 3]:
    url = f"http://127.0.0.1:5150/api/dre?ano=2026&mes={m}&emp=ALL&cenc=ALL"
    resp = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    print(f"\n==================== MÊS {m} / 2026 ====================")
    for b in resp["dre"]:
        if "Custo" in b["bloco"]:
            print(f"[{b['bloco']}]")
            print(f"  TOTAL BLOCO: Orçado = {b['orcado']:,.0f} | Realizado = {b['realizado']:,.0f} | % Orç = {b.get('pct_orc')}% | % Real = {b.get('pct_real')}% | R/O = {b.get('ro')}%")
            for t in b["titulos"]:
                print(f"    - {t['titulo']:<20}: Orçado = {t['orcado']:11,.0f} | Realizado = {t['realizado']:11,.0f} | % Orç = {t.get('pct_orc')}% | % Real = {t.get('pct_real')}% | R/O = {t.get('ro')}%")
