import subprocess
import sqlite3
import pandas as pd
import json

PORTS = [60216, 63263]

def run_dax(port, dax):
    ps_script = f"""
    [System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:{port};")
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = @"
{dax}
"@
    $adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
    $dt = New-Object System.Data.DataTable
    $adapter.Fill($dt) | Out-Null
    
    $result = @()
    foreach ($r in $dt.Rows) {{
        $obj = @{{}}
        foreach ($c in $dt.Columns) {{
            $obj[$c.ColumnName] = $r[$c.ColumnName]
        }}
        $result += $obj
    }}
    $conn.Close()
    $result | ConvertTo-Json -Depth 10
    """
    with open("temp_audit.ps1", "w", encoding="utf-8-sig") as f:
        f.write(ps_script)
    
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "temp_audit.ps1"], capture_output=True, text=True)
    try:
        return json.loads(res.stdout)
    except Exception as e:
        return None

dax = """
EVALUATE
SUMMARIZECOLUMNS(
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8),
    "REAL", [REALIZADO (R$)..],
    "ORC", [ORÇADO (R$).]
)
"""

pbi_data = None
for p in PORTS:
    res = run_dax(p, dax)
    if res and len(res) > 0 and 'VMQ_CADDRE[BLOCO]' in res[0]:
        pbi_data = res
        break

if not pbi_data:
    print("Could not get data from PowerBI")
    exit(1)

# SQLite
conn = sqlite3.connect('dre_cache.db')
sql = """
SELECT bloco, titulo, descrnat, sum(realizado) as real, sum(orcado) as orc
FROM dre_data
WHERE ano = 2026 AND mes = 8
GROUP BY bloco, titulo, descrnat
"""
sqlite_df = pd.read_sql(sql, conn)

pbi_dict = {}
for r in pbi_data:
    bloco = str(r.get('VMQ_CADDRE[BLOCO]', '')).strip()
    titulo = str(r.get('VMQ_CADDRE[TITULO]', '')).strip()
    nat = str(r.get('VMQ_TGFNAT[DESCRNAT]', '')).strip()
    key = f"{bloco}|{titulo}|{nat}"
    pbi_dict[key] = {
        'real': float(r.get('[REAL]', 0) or 0),
        'orc': float(r.get('[ORC]', 0) or 0)
    }

sqlite_dict = {}
for _, r in sqlite_df.iterrows():
    bloco = str(r['bloco']).strip()
    titulo = str(r['titulo']).strip()
    nat = str(r['descrnat']).strip()
    key = f"{bloco}|{titulo}|{nat}"
    sqlite_dict[key] = {
        'real': float(r['real'] or 0),
        'orc': float(r['orc'] or 0)
    }

diffs = []
all_keys = set(pbi_dict.keys()).union(set(sqlite_dict.keys()))

for k in all_keys:
    if k.endswith("|"):
        continue
    p_val = pbi_dict.get(k, {'real': 0.0, 'orc': 0.0})
    s_val = sqlite_dict.get(k, {'real': 0.0, 'orc': 0.0})
    
    diff_real = s_val['real'] - p_val['real']
    diff_orc = s_val['orc'] - p_val['orc']
    
    if abs(diff_real) > 1.0 or abs(diff_orc) > 1.0:
        parts = k.split('|')
        diffs.append({
            'Bloco': parts[0],
            'Titulo': parts[1],
            'Natureza': parts[2],
            'PBI_Real': p_val['real'],
            'SQLite_Real': s_val['real'],
            'Diff_Real': diff_real,
            'PBI_Orc': p_val['orc'],
            'SQLite_Orc': s_val['orc'],
            'Diff_Orc': diff_orc
        })

diffs = sorted(diffs, key=lambda x: abs(x['Diff_Real']), reverse=True)

md = "# Auditoria de Divergências (Agosto 2026)\n\n"
md += "Esta tabela mostra todas as divergências maiores que R$ 1.00 entre o SQLite e o PowerBI.\n\n"
md += "| Bloco | Título | Natureza | PBI Real | DB Real | Dif Real | PBI Orç | DB Orç | Dif Orç |\n"
md += "|---|---|---|---|---|---|---|---|---|\n"

for d in diffs:
    md += f"| {d['Bloco']} | {d['Titulo']} | {d['Natureza']} | {d['PBI_Real']:,.2f} | {d['SQLite_Real']:,.2f} | {d['Diff_Real']:,.2f} | {d['PBI_Orc']:,.2f} | {d['SQLite_Orc']:,.2f} | {d['Diff_Orc']:,.2f} |\n"

if not diffs:
    md += "Nenhuma divergência encontrada acima de R$ 1.00!"

with open("C:/Users/amello/.gemini/antigravity-ide/brain/f248ba37-4e86-4a15-b28d-7c97e84a98ca/auditoria_detalhada.md", "w", encoding="utf-8") as f:
    f.write(md)
print(f"Auditoria concluída. {len(diffs)} diferenças encontradas.")
