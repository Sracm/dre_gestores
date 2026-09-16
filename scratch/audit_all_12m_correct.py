import urllib.request
import json
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

ps = """
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:55192;Timeout=60;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    'Margem de Contribuição'[Item],
    VMQ_DREQLIK[MARGEM],
    VMQ_CADDRE[BLOCO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[CODEMP] <> 9),
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] <> 21010000),
    FILTER(VMQ_TSIEMP, NOT(VMQ_TSIEMP[RAZAOABREV] IN {"EA88 - SC", "EKOS - SP", "GLOBRAL - SC", "GLOBRAL - SP", "AGGP - SP"})),
    "ORC", [ORCAMENTO],
    "REAL", [REALIZADO.]
)
ORDER BY DCALENDARIO[NUMEROMES], VMQ_CADDRE[BLOCO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "PBI_DATA_START"
foreach ($r in $dt.Rows) {
    Write-Host ("{0}@@@{1}@@@{2}@@@{3}" -f $r[0], $r[3], $r[4], $r[5])
}
Write-Host "PBI_DATA_END"
$conn.Close()
"""

with open("scratch/get_pbi_all_12m.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/get_pbi_all_12m.ps1"], capture_output=True, text=True, encoding="utf-8")

pbi_data = {}
capture = False
for l in res.stdout.splitlines():
    if l.strip() == "PBI_DATA_START": capture = True; continue
    if l.strip() == "PBI_DATA_END": capture = False; continue
    if capture and "@@@" in l:
        p = l.split("@@@" )
        def pf(x):
            x = x.strip()
            if "," in x and "." in x: x = x.replace(".", "").replace(",", ".")
            elif "," in x: x = x.replace(",", ".")
            return float(x or 0)
        m = int(p[0])
        bloco = p[1].strip()
        pbi_data[(m, bloco)] = (pf(p[2]), pf(p[3]))

available_months = sorted(list(set(m for m, b in pbi_data.keys())))
print(f"Loaded records for months: {available_months}")

print("\n" + "=" * 125)
print(f"{'MÊS':<4} | {'BLOCO':<38} | {'ORC PBI':>12} | {'ORC API':>12} | {'DIFF ORC':>8} | {'REAL PBI':>12} | {'REAL API':>12} | {'DIFF REAL':>8} | {'STATUS'}")
print("=" * 125)

for m in available_months:
    url = f"http://127.0.0.1:5150/api/dre?ano=2026&mes={m}&emp=ALL&cenc=ALL"
    req = urllib.request.urlopen(url)
    api_resp = json.loads(req.read().decode('utf-8'))
    api_blocos = {b['bloco']: (b['orcado'], b['realizado']) for b in api_resp['dre']}
    
    # Margem
    po_vl, pr_vl = pbi_data.get((m, '1.Venda Liquida'), (0, 0))
    po_cmv, pr_cmv = pbi_data.get((m, '2.Custo Mercadoria Vendida'), (0, 0))
    pbi_margem_o = po_vl + po_cmv
    pbi_margem_r = pr_vl + pr_cmv
    
    ao_m, ar_m = api_blocos.get('MARGEM DE CONTRIBUIÇÃO', (0, 0))
    diff_mo = round(ao_m - pbi_margem_o)
    diff_mr = round(ar_m - pbi_margem_r)
    flag_m = "✅ OK" if abs(diff_mo) <= 1 and abs(diff_mr) <= 1 else "❌ DIFF"
    print(f"{m:<4} | {'MARGEM DE CONTRIBUIÇÃO':<38} | {pbi_margem_o:12,.0f} | {ao_m:12,.0f} | {diff_mo:8} | {pbi_margem_r:12,.0f} | {ar_m:12,.0f} | {diff_mr:8} | {flag_m}")

    for bloco in ['1.Venda Liquida', '2.Custo Mercadoria Vendida', '3.Despesas com Vendas', '4.Despesas Comercial Operacional', '5.Despesas Administrativa Operacional', '6.Receitas/Despesas Financeiras']:
        po, pr = pbi_data.get((m, bloco), (0, 0))
        ao, ar = api_blocos.get(bloco, (0, 0))
        do = round(ao - po)
        dr = round(ar - pr)
        flag = "✅ OK" if abs(do) <= 1 and abs(dr) <= 1 else "❌ DIFF"
        print(f"{m:<4} | {bloco:<38} | {po:12,.0f} | {ao:12,.0f} | {do:8} | {pr:12,.0f} | {ar:12,.0f} | {dr:8} | {flag}")
    print("-" * 125)
