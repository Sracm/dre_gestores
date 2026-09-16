$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

$dax = @'
EVALUATE
TOPN(50,
    SUMMARIZECOLUMNS(
        DCALENDARIO[ANO],
        DCALENDARIO[NOMEMES],
        VMQ_CADDRE[BLOCO],
        FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
        "ORCADO", [ORÇADO (R$).],
        "REALIZADO", [REALIZADO (R$)..]
    )
)
'@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "Success! Rows count: $($dt.Rows.Count)"
$rows = @()
foreach ($r in $dt.Rows) {
    $rows += [PSCustomObject]@{
        ANO = $r["ANO"]
        MES = $r["NOMEMES"]
        BLOCO = $r["BLOCO"]
        ORCADO = $r["ORCADO"]
        REALIZADO = $r["REALIZADO"]
    }
}
$rows | Format-Table -AutoSize | Out-String | Write-Host
$rows | ConvertTo-Json | Out-File -FilePath "benchmark_2026.json" -Encoding utf8

$conn.Close()
