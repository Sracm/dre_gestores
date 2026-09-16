import subprocess
import sqlite3
import json

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:63263;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    DCALENDARIO[TRI ANO],
    VMQ_TSICUS[CODCENCUS],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    VW_MQ_TGFPAR_POWER_BI[NOME],
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$rows = @()
foreach ($r in $dt.Rows) {
    $orc = 0.0
    if ($r["[ORCADO]"] -ne [DBNull]::Value) {
        $orc = [double]$r["[ORCADO]"]
    }
    $real = 0.0
    if ($r["[REALIZADO]"] -ne [DBNull]::Value) {
        $real = [double]$r["[REALIZADO]"]
    }
    
    $rows += [PSCustomObject]@{
        ano = [int]$r["DCALENDARIO[ANO]"]
        mes = [int]$r["DCALENDARIO[NUMEROMES]"]
        nomemes = [string]$r["DCALENDARIO[NOMEMES]"]
        tri_ano = [string]$r["DCALENDARIO[TRI ANO]"]
        codcencus = [int]$r["VMQ_TSICUS[CODCENCUS]"]
        bloco = [string]$r["VMQ_CADDRE[BLOCO]"]
        titulo = [string]$r["VMQ_CADDRE[TITULO]"]
        descrnat = [string]$r["VMQ_TGFNAT[DESCRNAT]"]
        parceiro = [string]$r["VW_MQ_TGFPAR_POWER_BI[NOME]"]
        orcado = $orc
        realizado = $real
    }
}
$conn.Close()

$rows | ConvertTo-Json -Depth 3 | Out-File -FilePath "$PWD/scratch/fsp_detalhe_exported.json" -Encoding utf8
Write-Host "Total rows exported:" $rows.Count
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("POWERSHELL OUTPUT:", res.stdout)
if res.stderr:
    print("POWERSHELL ERR:", res.stderr)

# Read json and insert to sqlite
try:
    with open('scratch/fsp_detalhe_exported.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
except Exception as e:
    print("Failed to read JSON:", e)
    exit(1)

conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS dre_detalhe_fsp")
cur.execute("""
CREATE TABLE dre_detalhe_fsp (
    ano INTEGER,
    mes INTEGER,
    nomemes TEXT,
    tri_ano TEXT,
    codcencus INTEGER,
    bloco TEXT,
    titulo TEXT,
    descrnat TEXT,
    parceiro TEXT,
    orcado REAL,
    realizado REAL
)
""")

insert_sql = """
INSERT INTO dre_detalhe_fsp (ano, mes, nomemes, tri_ano, codcencus, bloco, titulo, descrnat, parceiro, orcado, realizado)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

batch = []
for r in data:
    batch.append((
        r['ano'],
        r['mes'],
        r['nomemes'],
        r['tri_ano'],
        r.get('codcencus', 0),
        r['bloco'],
        r['titulo'],
        r['descrnat'],
        r['parceiro'],
        r['orcado'],
        r['realizado']
    ))

cur.executemany(insert_sql, batch)
cur.execute("CREATE INDEX idx_dre_detalhe_fsp_ano_mes ON dre_detalhe_fsp (ano, mes)")
cur.execute("CREATE INDEX idx_dre_detalhe_fsp_bloco ON dre_detalhe_fsp (bloco, titulo)")
cur.execute("CREATE INDEX idx_dre_detalhe_fsp_cenc ON dre_detalhe_fsp (codcencus)")
conn.commit()

print("Successfully inserted rows into dre_detalhe_fsp:", len(batch))
conn.close()
