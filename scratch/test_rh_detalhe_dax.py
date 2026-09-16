import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$dax = @"
EVALUATE
TOPN(
    50,
    CALCULATETABLE(
        SUMMARIZECOLUMNS(
            VMQ_CADDRE[BLOCO],
            VMQ_CADDRE[TITULO],
            VMQ_TGFNAT[DESCRNAT],
            VW_MQ_TGFPAR_POWER_BI[NOME],
            "ORCADO", [ORÇADO (R$).],
            "REALIZADO", [REALIZADO (R$)..]
        ),
        VMQ_TSICUS[CODCENCUS] = 9010000,
        DCALENDARIO[ANO] = 2026
    )
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "Total rows fetched:" $dt.Rows.Count
$dt | Format-Table -AutoSize

$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
