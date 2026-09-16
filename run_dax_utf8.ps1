
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO", [ORÇADO (R$).]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$list = @()
foreach ($r in $dt.Rows) {
    $list += [PSCustomObject]@{
        ANO = $r["ANO"]
        MES = $r["NOMEMES"]
        BLOCO = $r["BLOCO"]
        REALIZADO = $r["REALIZADO"]
        ORCADO = $r["ORCADO"]
    }
}
$list | ConvertTo-Json -Depth 3 | Out-File -FilePath "live_dax_result_2026.json" -Encoding utf8
Write-Host "Exported $($dt.Rows.Count) rows to live_dax_result_2026.json"
$conn.Close()
