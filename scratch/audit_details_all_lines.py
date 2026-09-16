import urllib.request
import json
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Query Power BI for all Titulos in 2026 months 1, 2, 3
ps = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:55192;Timeout=30;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] IN {1, 2, 3}),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[CODEMP] <> 9),
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] <> 21010000),
    FILTER(VMQ_TSIEMP, NOT(VMQ_TSIEMP[RAZAOABREV] IN {"EA88 - SC", "EKOS - SP", "GLOBRAL - SC", "GLOBRAL - SP", "AGGP - SP"})),
    "ORC", [ORCAMENTO],
    "REAL", [REALIZADO.]
)
ORDER BY DCALENDARIO[NUMEROMES], VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "PBI_DATA_START"
foreach ($r in $dt.Rows) {
    Write-Host ("{0}@@@{1}@@@{2}@@@{3}@@@{4}" -f $r[0], $r[1], $r[2], $r[3], $r[4])
}
Write-Host "PBI_DATA_END"
$conn.Close()
"""

with open("scratch/get_pbi_all_titulos.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/get_pbi_all_titulos.ps1"], capture_output=True, text=True)

pbi_titulos = {}
capture = False
for l in res.stdout.splitlines():
    if l.strip() == "PBI_DATA_START": capture = True; continue
    if l.strip() == "PBI_DATA_END": capture = False; continue
    if capture and "@@@" in l:
        p = l.split("@@@")
        def pf(x):
            x = x.strip()
            if "," in x and "." in x: x = x.replace(".", "").replace(",", ".")
            elif "," in x: x = x.replace(",", ".")
            return float(x or 0)
        m = int(p[0])
        bloco = p[1].strip()
        titulo = p[2].strip()
        pbi_titulos[(m, bloco, titulo)] = (pf(p[3]), pf(p[4]))

print(f"Loaded {len(pbi_titulos)} distinct month-bloco-titulo records from Power BI.\n")

# Now query API for months 1, 2, 3 and verify every single titulo
all_ok = True
for m in [1, 2, 3]:
    url = f"http://127.0.0.1:5150/api/dre?ano=2026&mes={m}&emp=ALL&cenc=ALL"
    req = urllib.request.urlopen(url)
    api_resp = json.loads(req.read().decode('utf-8'))
    
    # Flatten API titulos
    api_titulos = {}
    for b in api_resp['dre']:
        bloco_name = b['bloco']
        for t in b.get('titulos', []):
            api_titulos[(m, bloco_name, t['titulo'])] = (t['orcado'], t['realizado'])
            
    print("=" * 135)
    print(f"--- MÊS {m} / 2026 ---")
    print(f"{'BLOCO':<32} | {'TÍTULO':<32} | {'ORÇ PBI':>12} | {'ORÇ API':>12} | {'D_ORÇ':>6} | {'REAL PBI':>12} | {'REAL API':>12} | {'D_RL':>6} | STATUS")
    print("-" * 135)
    
    # All unique (bloco, titulo) keys for this month from either PBI or API
    keys = sorted(set([k for k in pbi_titulos.keys() if k[0] == m] + [k for k in api_titulos.keys() if k[0] == m]))
    for _, bloco, titulo in keys:
        po, pr = pbi_titulos.get((m, bloco, titulo), (0, 0))
        ao, ar = api_titulos.get((m, bloco, titulo), (0, 0))
        d_orc = round(ao - po)
        d_real = round(ar - pr)
        status = "OK" if abs(d_orc) <= 1 and abs(d_real) <= 1 else "DIFF"
        if status == "DIFF":
            all_ok = False
        print(f"{bloco[:32]:<32} | {titulo[:32]:<32} | {po:12,.0f} | {ao:12,.0f} | {d_orc:6} | {pr:12,.0f} | {ar:12,.0f} | {d_real:6} | {'✅' if status == 'OK' else '❌ ' + status}")

print("\n" + "=" * 50)
if all_ok:
    print("RESULTADO FINAL: TODOS OS TÍTULOS BATENDO 100%!")
else:
    print("RESULTADO: ENCONTRADAS DIVERGÊNCIAS NOS TÍTULOS ACIMA.")
print("=" * 50)
