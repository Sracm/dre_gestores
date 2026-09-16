
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

$dax = @"
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

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$list = @()
foreach ($r in $dt.Rows) {
    $list += [PSCustomObject]@{
        BLOCO = $r["VMQ_CADDRE[BLOCO]"]
        TITULO = $r["VMQ_CADDRE[TITULO]"]
        REALIZADO = $r["[REALIZADO]"]
        ORCADO = $r["[ORCADO]"]
    }
}
$list | ConvertTo-Json | Out-File -FilePath "dax_live_result.json" -Encoding utf8
$conn.Close()
Write-Host "Done querying live DAX JSON!"
