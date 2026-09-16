
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 52578
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=15;")
$conn.Open()

# Query Venda Bruta por Empresa em Março/2026
$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    VMQ_TSIEMP[CODEMP],
    VMQ_TSIEMP[RAZAOABREV],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 3),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[TITULO] = "1.Venda Bruta"),
    "REALIZADO_GESTORES", [REALIZADO (R$)..],
    "REALIZADO_EMPRESA", [REALIZADO.],
    "ORCADO", [ORÇADO (R$).]
)
ORDER BY VMQ_TSIEMP[CODEMP]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$rows = @()
foreach ($r in $dt.Rows) {
    $rows += [PSCustomObject]@{
        CODEMP = $r[0]
        RAZAOABREV = $r[1].ToString()
        Real_Gestores = $r[2]
        Real_Empresa = $r[3]
        Orcado = $r[4]
    }
}
$rows | ConvertTo-Json -Depth 3 | Out-File -FilePath "vb_by_empresa_mar2026.json" -Encoding utf8
$conn.Close()
Write-Host "Done!"
