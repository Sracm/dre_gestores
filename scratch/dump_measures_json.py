import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [Name], [Expression] FROM `$SYSTEM.TMSCHEMA_MEASURES WHERE [Name] = '..' OR [Name] = 'teste antonio 2' OR [Name] = 'R/O'"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$out = @{}
foreach ($row in $dt.Rows) {
    $out[$row["Name"]] = $row["Expression"]
}
$out | ConvertTo-Json | Out-File -FilePath "$PWD/scratch/measures_out.json" -Encoding utf8
$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDERR:", res.stderr)
