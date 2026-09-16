[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:55192;Timeout=30;")
$conn.Open()
$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    'Margem de Contribuição'[Item],
    VMQ_DREQLIK[MARGEM],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] = "6.Receitas/Despesas Financeiras"),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[CODEMP] <> 9),
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] <> 21010000),
    FILTER(VMQ_TSIEMP, NOT(VMQ_TSIEMP[RAZAOABREV] IN {"EA88 - SC", "EKOS - SP", "GLOBRAL - SC", "GLOBRAL - SP", "AGGP - SP"})),
    "ORC", [ORCAMENTO],
    "REAL", [REALIZADO.]
)
"@
$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
foreach ($r in $dt.Rows) {
    Write-Host ("{0} | ORC: {1} | REAL: {2}" -f $r[3], $r[4], $r[5])
}
$conn.Close()
