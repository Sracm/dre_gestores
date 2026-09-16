import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$dax = @"
EVALUATE
TOPN(
    10,
    SUMMARIZECOLUMNS(
        DCALENDARIO[ANO],
        DCALENDARIO[NUMEROMES],
        VMQ_CADDRE[BLOCO],
        FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
        "ORCADO", [ORÇADO (R$).],
        "REALIZADO", [REALIZADO (R$)..]
    )
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

foreach ($c in $dt.Columns) {
    Write-Host "COL:" $c.ColumnName
}
foreach ($r in $dt.Rows) {
    Write-Host "ROW: $($r[0]) | $($r[1]) | $($r[2]) | ORC: $($r['[ORCADO]']) | REAL: $($r['[REALIZADO]'])"
}
$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print(res.stdout)
print("ERR:", res.stderr)
