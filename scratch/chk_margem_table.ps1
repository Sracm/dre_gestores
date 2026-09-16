[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:55192;Timeout=30;")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = "EVALUATE 'Margem de Contribuição'"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
Write-Host ("Rows: " + $dt.Rows.Count)
foreach ($r in $dt.Rows) {
    Write-Host ($r[0].ToString() + " | " + $r[1].ToString())
}
$conn.Close()
