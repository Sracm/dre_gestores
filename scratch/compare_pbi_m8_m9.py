import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

# Let's query the DAX measures for Agosto and Setembro 2026 for RH (codcencus = 9010000)
$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && (DCALENDARIO[NUMEROMES] = 8 || DCALENDARIO[NUMEROMES] = 9)),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO_RAW", [ORCAMENTO],
    "REALIZADO_RAW", [SOMA REALIZADO]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$lines = @()
foreach ($r in $dt.Rows) {
    $lines += "Mes: $($r['DCALENDARIO[NUMEROMES]']) ($($r['DCALENDARIO[NOMEMES]'])) | Bloco: $($r['VMQ_CADDRE[BLOCO]']) | Tit: $($r['VMQ_CADDRE[TITULO]']) | Nat: $($r['VMQ_TGFNAT[DESCRNAT]']) | Orc: $($r['[ORCADO]']) | Real: $($r['[REALIZADO]'])"
}

$conn.Close()
$lines | Out-File -FilePath "$PWD/scratch/pbi_m8_m9_compare.txt" -Encoding utf8
Write-Host "Total rows: $($lines.Count)"
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print(res.stdout)
