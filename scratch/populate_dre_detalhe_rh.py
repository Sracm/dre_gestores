import subprocess
import sqlite3
import json

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    DCALENDARIO[TRI ANO],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    VW_MQ_TGFPAR_POWER_BI[NOME],
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
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
        bloco = [string]$r["VMQ_CADDRE[BLOCO]"]
        titulo = [string]$r["VMQ_CADDRE[TITULO]"]
        descrnat = [string]$r["VMQ_TGFNAT[DESCRNAT]"]
        parceiro = [string]$r["VW_MQ_TGFPAR_POWER_BI[NOME]"]
        orcado = $orc
        realizado = $real
    }
}
$conn.Close()

$rows | ConvertTo-Json -Depth 3 | Out-File -FilePath "$PWD/scratch/rh_detalhe_exported.json" -Encoding utf8
Write-Host "Total rows exported:" $rows.Count
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("POWERSHELL OUTPUT:", res.stdout)
if res.stderr:
    print("POWERSHELL ERR:", res.stderr)

# Read json and insert to sqlite
with open('scratch/rh_detalhe_exported.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS dre_detalhe_rh")
cur.execute("""
CREATE TABLE dre_detalhe_rh (
    ano INTEGER,
    mes INTEGER,
    nomemes TEXT,
    tri_ano TEXT,
    bloco TEXT,
    titulo TEXT,
    descrnat TEXT,
    parceiro TEXT,
    orcado REAL,
    realizado REAL
)
""")

insert_sql = """
INSERT INTO dre_detalhe_rh (ano, mes, nomemes, tri_ano, bloco, titulo, descrnat, parceiro, orcado, realizado)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

batch = []
for r in data:
    batch.append((
        r['ano'],
        r['mes'],
        r['nomemes'],
        r['tri_ano'],
        r['bloco'],
        r['titulo'],
        r['descrnat'],
        r['parceiro'],
        r['orcado'],
        r['realizado']
    ))

cur.executemany(insert_sql, batch)
cur.execute("CREATE INDEX idx_dre_detalhe_rh_ano_mes ON dre_detalhe_rh (ano, mes)")
cur.execute("CREATE INDEX idx_dre_detalhe_rh_bloco ON dre_detalhe_rh (bloco, titulo)")
conn.commit()

print("Successfully inserted rows into dre_detalhe_rh:", len(batch))

# Verify
cur.execute("SELECT ano, COUNT(*), SUM(orcado), SUM(realizado) FROM dre_detalhe_rh GROUP BY ano ORDER BY ano")
for row in cur.fetchall():
    print(f"Ano {row[0]}: count={row[1]}, orcado={row[2]:,.2f}, realizado={row[3]:,.2f}")

conn.close()
