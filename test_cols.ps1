
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

$dax = @"
EVALUATE
TOPN(10,
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

Write-Host "Columns in DataTable:"
foreach ($col in $dt.Columns) {
    Write-Host "  COLNAME: $($col.ColumnName)"
}

Write-Host "Sample Rows:"
for ($i = 0; $i -lt [Math]::Min(5, $dt.Rows.Count); $i++) {
    $row = $dt.Rows[$i]
    Write-Host "--- Row $i ---"
    foreach ($col in $dt.Columns) {
        Write-Host "  $($col.ColumnName) = $($row[$col.ColumnName])"
    }
}

$conn.Close()
