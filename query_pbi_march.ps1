$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

Write-Host "Connected to Power BI on port 58493!"

# Let's query exactly what the Matrix Visual queries for Março/2026:
$dax1 = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NOMEMES] = "mar"),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..],
    "% VB ORCADO", [%s/ VB orçado],
    "% VB REALIZADO", [%s/ VB REALIZADO],
    "R_O", [R/O]
)
ORDER BY VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax1
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "`n--- RESULTADOS NÍVEL BLOCO E TÍTULO (MARÇO/2026) ---"
foreach ($r in $dt.Rows) {
    Write-Host ("{0,-35} | {1,-35} | Real: {2,14:N2} | Orc: {3,14:N2}" -f $r["VMQ_CADDRE[BLOCO]"], $r["VMQ_CADDRE[TITULO]"], $r["REALIZADO"], $r["ORCADO"])
}

# Also at Bloco level:
$dax2 = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NOMEMES] = "mar"),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..],
    "R_O", [R/O]
)
ORDER BY VMQ_CADDRE[BLOCO]
"@

$cmd.CommandText = $dax2
$dt2 = New-Object System.Data.DataTable
$adapter.Fill($dt2) | Out-Null

Write-Host "`n--- RESULTADOS NÍVEL BLOCO (MARÇO/2026) ---"
foreach ($r in $dt2.Rows) {
    Write-Host ("{0,-40} | Real: {1,14:N2} | Orc: {2,14:N2}" -f $r["VMQ_CADDRE[BLOCO]"], $r["REALIZADO"], $r["ORCADO"])
}

$conn.Close()
