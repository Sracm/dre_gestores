import json

with open('scratch/rh_detalhe_full.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

by_year = {}
for r in data:
    y = r['ano']
    if y not in by_year:
        by_year[y] = {'count': 0, 'orcado': 0.0, 'realizado': 0.0}
    by_year[y]['count'] += 1
    by_year[y]['orcado'] += r['orcado']
    by_year[y]['realizado'] += r['realizado']

for y, v in sorted(by_year.items()):
    c = v['count']
    o = v['orcado']
    re = v['realizado']
    print(f"Year {y}: rows={c}, orcado={o:,.2f}, realizado={re:,.2f}")
