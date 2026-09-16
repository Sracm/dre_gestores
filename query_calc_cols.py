import subprocess

ps = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [TableID], [ExplicitName], [Expression] FROM `$SYSTEM.TMSCHEMA_COLUMNS WHERE [Type] = 2"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

foreach ($r in $dt.Rows) {
    Write-Host "COL: $($r['ExplicitName'])"
    Write-Host "EXPR: $($r['Expression'])"
    Write-Host "---------------------------"
}
$conn.Close()
"""

with open("get_calc_cols.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "get_calc_cols.ps1"], capture_output=True, text=True, encoding="utf-8-sig")
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
