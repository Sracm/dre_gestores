
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 52578
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=30;")
$conn.Open()

# 1. GESTORES: Mes a mes por Bloco e Titulo em 2026
$daxGestores = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] <> 21010000),
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO", [ORÇADO (R$).]
)
ORDER BY DCALENDARIO[NUMEROMES], VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $daxGestores
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dtG = New-Object System.Data.DataTable
$adapter.Fill($dtG) | Out-Null

$rowsG = @()
foreach ($r in $dtG.Rows) {
    $rowsG += [PSCustomObject]@{
        Mes = [int]$r["DCALENDARIO[NUMEROMES]"]
        Bloco = $r["VMQ_CADDRE[BLOCO]"].ToString()
        Titulo = $r["VMQ_CADDRE[TITULO]"].ToString()
        Realizado = if ($r["[REALIZADO]"] -ne [DBNull]::Value) { [double]$r["[REALIZADO]"] } else { 0.0 }
        Orcado = if ($r["[ORCADO]"] -ne [DBNull]::Value) { [double]$r["[ORCADO]"] } else { 0.0 }
    }
}
$rowsG | ConvertTo-Json -Depth 3 | Out-File -FilePath "audit_pbi_gestores.json" -Encoding utf8

# 2. EMPRESA: Mes a mes por Bloco e Titulo em 2026
$daxEmpresa = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    "REALIZADO", [REALIZADO.],
    "ORCADO", [ORCAMENTO]
)
ORDER BY DCALENDARIO[NUMEROMES], VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd.CommandText = $daxEmpresa
$dtE = New-Object System.Data.DataTable
$adapter.Fill($dtE) | Out-Null

$rowsE = @()
foreach ($r in $dtE.Rows) {
    $rowsE += [PSCustomObject]@{
        Mes = [int]$r["DCALENDARIO[NUMEROMES]"]
        Bloco = $r["VMQ_CADDRE[BLOCO]"].ToString()
        Titulo = $r["VMQ_CADDRE[TITULO]"].ToString()
        Realizado = if ($r["[REALIZADO]"] -ne [DBNull]::Value) { [double]$r["[REALIZADO]"] } else { 0.0 }
        Orcado = if ($r["[ORCADO]"] -ne [DBNull]::Value) { [double]$r["[ORCADO]"] } else { 0.0 }
    }
}
$rowsE | ConvertTo-Json -Depth 3 | Out-File -FilePath "audit_pbi_empresa.json" -Encoding utf8

$conn.Close()
Write-Host "Extração Power BI concluída: Gestores=$($rowsG.Count) linhas, Empresa=$($rowsE.Count) linhas."
