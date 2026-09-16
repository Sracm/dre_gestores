$dax = "SELECT MEASURE_NAME FROM `$SYSTEM.MDSCHEMA_MEASURES"
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:64795;")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$dt | Select-Object -ExpandProperty MEASURE_NAME | Where-Object { $_ -match "OR" -or $_ -match "REALIZADO" }
