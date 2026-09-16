
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

$dax = @"
EVALUATE
TOPN(
    10,
    SUMMARIZECOLUMNS(
        DCALENDARIO[ANO],
        DCALENDARIO[NOMEMES],
        VMQ_CADDRE[BLOCO],
        FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
        "REALIZADO", [REALIZADO (R$)..],
        "ORCADO", [ORÇADO (R$).]
    )
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "COLUMNS:"
foreach ($c in $dt.Columns) {
    Write-Host " - $($c.ColumnName)"
}

Write-Host "`nSAMPLE ROWS:"
foreach ($r in $dt.Rows) {
    $vals = @()
    foreach ($c in $dt.Columns) {
        $vals += "$($c.ColumnName)=$($r[$c.ColumnName])"
    }
    Write-Host ($vals -join " | ")
}

$conn.Close()
