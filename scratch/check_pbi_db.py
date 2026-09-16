import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()
Write-Host "Database Name:" $conn.Database

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [CATALOG_NAME], [DESCRIPTION] FROM $SYSTEM.DBSCHEMA_CATALOGS"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$dt | Format-Table

$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
