import subprocess

ps = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [MEASUREGROUP_NAME], [MEASURE_NAME], [EXPRESSION] FROM `$SYSTEM.MDSCHEMA_MEASURES WHERE [MEASUREGROUP_NAME] = 'MEDIDAS' OR [MEASUREGROUP_NAME] = 'DRE GESTORES'"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
foreach ($r in $dt.Rows) {
    Write-Host "MEASURE: $($r['MEASURE_NAME'])"
    Write-Host "EXPR: $($r['EXPRESSION'])"
    Write-Host "----------------------------------"
}
$conn.Close()
"""
with open("get_measures.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "get_measures.ps1"], capture_output=True, text=True, encoding="utf-8-sig")
with open("pbi_measures_all.txt", "w", encoding="utf-8") as f:
    f.write(res.stdout)
print("Done! Measures count characters:", len(res.stdout))
