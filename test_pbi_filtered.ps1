
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 52578

try {
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=10;")
    $conn.Open()
    Write-Host "Connected to port $port!"

    # Allowed companies
    # Exclude CODEMP = 9 and CODCENCUS = 21010000
    $dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[CODEMP] <> 9 && VMQ_TSIEMP[RAZAOABREV] IN {
        "FORX", "MCR - FABRICA", "MCR - FILIAL 03", 
        "MCR - MATRIZ", "MCR - SC", "QUALITY - RJ", "QUALITY MATRIZ", 
        "SL ONLINE - SP", "VLS - RJ", "VLS - SP", "FORX MG"
    }),
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] <> 21010000),
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
    
    Write-Host "Rows returned: $($dt.Rows.Count)"
    $res = @()
    foreach ($r in $dt.Rows) {
        $res += [PSCustomObject]@{
            Bloco = $r[0].ToString()
            Titulo = $r[1].ToString()
            Realizado = $r[2]
            Orcado = $r[3]
        }
    }
    $res | ConvertTo-Json -Depth 3 | Out-File -FilePath "pbi_gestores_filtered_ago2026.json" -Encoding utf8
    Write-Host "Saved pbi_gestores_filtered_ago2026.json!"
    $conn.Close()
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
