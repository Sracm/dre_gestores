import urllib.request
import json

req = urllib.request.urlopen('http://127.0.0.1:5100/api/dre/detalhe?ano=2026&mes=9')
data = json.loads(req.read().decode('utf-8'))
print('STATUS:', data['status'])
print('MESES SELECIONADOS:', data['meses_selecionados'])

def print_tree(nodes, depth=0):
    indent = '  ' * depth
    for n in nodes:
        orc = n['total_orcado']
        real = n['total_realizado']
        print(f"{indent}[L{n['level']}] {n['nome']} | Orc: {orc:,.2f} | Real: {real:,.2f}")
        if 'filhos' in n and n['filhos']:
            print_tree(n['filhos'], depth + 1)

print_tree(data['tree'])
