import subprocess
import sqlite3
import pandas as pd
import os
import json

valid_port = 60886

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:""" + str(valid_port) + """;")
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
    FILTER(DCALENDARIO, DCALENDARIO[ANO] >= 2025),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$conn.Close()

$dt | Export-Csv -Path "$PWD/scratch/fsp_detalhe_exported.csv" -NoTypeInformation -Encoding UTF8
Write-Host "Export finished."
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("POWERSHELL OUTPUT:", res.stdout)
if res.stderr:
    print("POWERSHELL ERR:", res.stderr)

csv_file = 'scratch/fsp_detalhe_exported.csv'
if not os.path.exists(csv_file):
    print("CSV file not found!")
    exit(1)

df = pd.read_csv(csv_file)
conn = sqlite3.connect('dre_cache.db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS dre_detalhe_fsp")
conn.commit()

df = df.rename(columns={
    'DCALENDARIO[ANO]': 'ano',
    'DCALENDARIO[NUMEROMES]': 'mes',
    'DCALENDARIO[NOMEMES]': 'nomemes',
    'DCALENDARIO[TRI ANO]': 'tri_ano',
    'VMQ_TSICUS[CODCENCUS]': 'codcencus',
    'VMQ_CADDRE[BLOCO]': 'bloco',
    'VMQ_CADDRE[TITULO]': 'titulo',
    'VMQ_TGFNAT[DESCRNAT]': 'descrnat',
    'VW_MQ_TGFPAR_POWER_BI[NOME]': 'parceiro',
    '[ORCADO]': 'orcado',
    '[REALIZADO]': 'realizado'
})

columns_to_keep = ['ano', 'mes', 'nomemes', 'tri_ano', 'codcencus', 'bloco', 'titulo', 'descrnat', 'parceiro', 'orcado', 'realizado']
df = df[[c for c in df.columns if c in columns_to_keep]]
df['orcado'] = df['orcado'].fillna(0.0)
df['realizado'] = df['realizado'].fillna(0.0)

df.to_sql('dre_detalhe_fsp', conn, index=False)

cur.execute("CREATE INDEX idx_dre_detalhe_fsp_ano_mes ON dre_detalhe_fsp (ano, mes)")
cur.execute("CREATE INDEX idx_dre_detalhe_fsp_bloco ON dre_detalhe_fsp (bloco, titulo)")
cur.execute("CREATE INDEX idx_dre_detalhe_fsp_cenc ON dre_detalhe_fsp (codcencus)")
conn.commit()

print(f"Successfully inserted {len(df)} rows into dre_detalhe_fsp")
conn.close()
