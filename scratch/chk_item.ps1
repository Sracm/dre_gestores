
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Reflection.Assembly]::LoadFrom('C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll') | Out-Null
 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection('Data Source=localhost:55192;Timeout=30;')
.Open()
 = .CreateCommand()
.CommandText = 'EVALUATE VALUES(''Margem de Contribuição''[Item])'
 = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter()
 = New-Object System.Data.DataTable
.Fill() | Out-Null
foreach ( in .Rows) { Write-Host [0] }
.Close()
