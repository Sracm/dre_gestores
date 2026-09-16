import urllib.request
import json

url = "http://127.0.0.1:5100/api/dre?ano=2026&mes=3&emp=ALL&cenc=ALL"

try:
    req = urllib.request.urlopen(url, timeout=10)
    data = json.loads(req.read().decode("utf-8"))
    dre = data.get("dre", [])
    print(f"Total items in dre: {len(dre)}")
    for item in dre:
        bloco = item.get("bloco")
        orc = item.get("orcado", 0)
        real = item.get("realizado", 0)
        p_orc = item.get("pct_orc")
        p_real = item.get("pct_real")
        ro = item.get("ro")
        print(f"{bloco:<35} | Orc: {orc:>12,.0f} | Real: {real:>12,.0f} | % Orç: {str(p_orc)+'%':>7} | % Real: {str(p_real)+'%':>7} | R/O: {str(ro)+'%' if ro is not None else '-':>7}")
        for t in item.get("titulos", []):
            t_name = t.get("titulo")
            t_orc = t.get("orcado", 0)
            t_real = t.get("realizado", 0)
            t_ro = t.get("ro")
            print(f"  {t_name:<33} | Orc: {t_orc:>12,.0f} | Real: {t_real:>12,.0f} | R/O: {str(t_ro)+'%' if t_ro is not None else '-':>7}")
except Exception as e:
    print("Error querying endpoint:", e)
