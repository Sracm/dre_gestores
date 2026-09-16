import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "EVALUATE INFO.TABLES()"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "Tables in Active Model:"
$dt | Select-Object Name | Format-Table -AutoSize

$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
