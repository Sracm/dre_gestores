
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

# 1. Por Bloco em Março/2026
$dax1 = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NOMEMES] = "mar"),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO", [ORÇADO (R$).]
)
ORDER BY VMQ_CADDRE[BLOCO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax1
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "=== PBI LIVE: NÍVEL BLOCO (MARÇO/2026) ==="
foreach ($r in $dt.Rows) {
    Write-Host ("{0,-40} | Real: {1,14:N2} | Orc: {2,14:N2}" -f $r["BLOCO"], $r["REALIZADO"], $r["ORCADO"])
}

# 2. Por Titulo em Março/2026
$dax2 = @"
EVALUATE
SUMMARIZECOLUMNS(
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NOMEMES] = "mar"),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO", [ORÇADO (R$).]
)
ORDER BY VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd.CommandText = $dax2
$dt2 = New-Object System.Data.DataTable
$adapter.Fill($dt2) | Out-Null

Write-Host "`n=== PBI LIVE: NÍVEL TÍTULO (MARÇO/2026) ==="
foreach ($r in $dt2.Rows) {
    Write-Host ("{0,-35} | {1,-35} | Real: {2,14:N2} | Orc: {3,14:N2}" -f $r["BLOCO"], $r["TITULO"], $r["REALIZADO"], $r["ORCADO"])
}

$conn.Close()
