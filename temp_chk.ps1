
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 52616
try {
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=5;")
    $conn.Open()
    Write-Host "PORT $port CONNECTED!"
    
    # Query tables
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT [TABLE_NAME] FROM `$SYSTEM.DBSCHEMA_TABLES WHERE [TABLE_TYPE] = 'TABLE'"
    $r = $cmd.ExecuteReader()
    $tbls = @()
    while ($r.Read()) {
        $t = $r[0].ToString()
        if (-not $t.StartsWith("LocalDateTable") -and -not $t.StartsWith("DateTableTemplate")) {
            $tbls += $t
        }
    }
    $r.Close()
    Write-Host "TABLES: $($tbls -join ', ')"

    # Query sample measures
    $cmd.CommandText = "SELECT TOP 10 [MEASURE_NAME] FROM `$SYSTEM.MDSCHEMA_MEASURES"
    $r = $cmd.ExecuteReader()
    $ms = @()
    while ($r.Read()) {
        $ms += $r[0].ToString()
    }
    $r.Close()
    Write-Host "SAMPLE_MEASURES: $($ms -join ', ')"
    $conn.Close()
} catch {
    Write-Host "PORT $port ERROR: $($_.Exception.Message)"
}
