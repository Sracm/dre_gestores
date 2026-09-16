
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

# Lista tabelas e contagem de linhas
$dax = "EVALUATE ROW('Count', COUNTROWS(VMQ_DREQLIK))"
$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$count = $cmd.ExecuteScalar()
Write-Host "Linhas em VMQ_DREQLIK no Power BI: $count"

$conn.Close()
