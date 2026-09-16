import subprocess

for port in [58493, 51906]:
    ps = f"""
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:{port};")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$names = ($dt.Rows | ForEach-Object {{ $_["Name"] }}) -join ", "
Write-Host "PORT {port} TABLES: $names"
$conn.Close()
"""
    with open("list_tables.ps1", "w", encoding="utf-8-sig") as f:
        f.write(ps)
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "list_tables.ps1"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("ERR:", res.stderr)
