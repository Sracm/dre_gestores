
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 52578

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=10;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [MEASUREGROUP_NAME], [MEASURE_NAME], [EXPRESSION] FROM `$SYSTEM.MDSCHEMA_MEASURES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$list = @()
foreach ($r in $dt.Rows) {
    if ($r["EXPRESSION"] -ne $null -and $r["EXPRESSION"].ToString().Trim() -ne "") {
        $list += [PSCustomObject]@{
            Table = $r["MEASUREGROUP_NAME"].ToString()
            Measure = $r["MEASURE_NAME"].ToString()
            Expression = $r["EXPRESSION"].ToString()
        }
    }
}

$list | ConvertTo-Json -Depth 4 | Out-File -FilePath "all_live_measures.json" -Encoding utf8
Write-Host "Exported $($list.Count) measures with expressions!"
$conn.Close()
