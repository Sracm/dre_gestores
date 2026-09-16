
    [System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:63263;")
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = @"

EVALUATE
SUMMARIZECOLUMNS(
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 8),
    "REAL", [REALIZADO (R$)..],
    "ORC", [ORÇADO (R$).]
)

"@
    $adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
    $dt = New-Object System.Data.DataTable
    $adapter.Fill($dt) | Out-Null
    
    $result = @()
    foreach ($r in $dt.Rows) {
        $obj = @{}
        foreach ($c in $dt.Columns) {
            $obj[$c.ColumnName] = $r[$c.ColumnName]
        }
        $result += $obj
    }
    $conn.Close()
    $result | ConvertTo-Json -Depth 10
    