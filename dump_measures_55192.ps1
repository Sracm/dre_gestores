
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:55192;Timeout=15;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [TableID], [Name], [Expression] FROM `$SYSTEM.TMSCHEMA_MEASURES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$out = @()
foreach ($r in $dt.Rows) {
    $out += "MEASURE: $($r['Name'])`r`n$($r['Expression'])`r`n--------------------------------------------------"
}
[System.IO.File]::WriteAllLines("$PWD\all_measures_55192.txt", $out)
Write-Host "Wrote $($dt.Rows.Count) measures to all_measures_55192.txt"

$conn.Close()
