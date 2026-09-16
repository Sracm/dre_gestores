import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [Name], [Expression] FROM `$SYSTEM.TMSCHEMA_MEASURES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

foreach ($row in $dt.Rows) {
    if ($row["Name"] -eq ".." -or $row["Name"] -eq "teste antonio 2") {
        Write-Host "==============================="
        Write-Host "MEASURE:" $row["Name"]
        Write-Host "EXPRESSION:" $row["Expression"]
    }
}

$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
