$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

# Execute DAX query on port 60775 to get exact summary numbers for recent period (e.g. ANO = 2026 or 2025)
$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..],
    "% VB ORCADO", [%s/ VB orçado],
    "% VB REALIZADO", [%s/ VB REALIZADO],
    "R_O", [R/O]
)
ORDER BY DCALENDARIO[ANO], DCALENDARIO[NOMEMES], VMQ_CADDRE[BLOCO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "Returned $($dt.Rows.Count) rows from live Power BI model:"
$results = @()
foreach ($r in $dt.Rows) {
    $results += [PSCustomObject]@{
        ANO = $r["ANO"]
        MES = $r["NOMEMES"]
        BLOCO = $r["BLOCO"]
        ORCADO = $r["ORCADO"]
        REALIZADO = $r["REALIZADO"]
        PCT_ORC = $r["% VB ORCADO"]
        PCT_REAL = $r["% VB REALIZADO"]
        R_O = $r["R_O"]
    }
}

$results | ConvertTo-Json -Depth 4 | Out-File -FilePath "live_pbi_benchmark.json" -Encoding utf8
Write-Host "Exported live_pbi_benchmark.json!"

$conn.Close()
