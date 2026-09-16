
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$ports = @(52578, 52579, 52598, 52615, 52616)

foreach ($port in $ports) {
    try {
        $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=5;")
        $conn.Open()
        
        # Test query
        $dax = @"
EVALUATE
ROW(
    "VB_REAL", CALCULATE([REALIZADO (R$)..], FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8), FILTER(VMQ_CADDRE, VMQ_CADDRE[TITULO] = "1.Venda Bruta")),
    "VB_ORC", CALCULATE([ORÇADO (R$).], FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8), FILTER(VMQ_CADDRE, VMQ_CADDRE[TITULO] = "1.Venda Bruta"))
)
"@
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = $dax
        $adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
        $dt = New-Object System.Data.DataTable
        $adapter.Fill($dt) | Out-Null
        
        Write-Host "PORT $port -> VB_REAL: $($dt.Rows[0]['[VB_REAL]']) | VB_ORC: $($dt.Rows[0]['[VB_ORC]'])"
        $conn.Close()
    } catch {
        Write-Host "PORT $port ERROR: $($_.Exception.Message)"
    }
}
