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
    $n = [string]$row["Name"]
    if ($n -like "*antonio*" -or $n -like "*TESTE.*" -or $n -eq ".." -or $n -like "*REALIZADO (R$)*" -or $n -like "*ORÇADO (R$)*") {
        Write-Host "==============================="
        Write-Host "MEASURE:" $n
        Write-Host "EXPRESSION:" $row["Expression"]
    }
}

$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
with open('scratch/found_measures.txt', 'w', encoding='utf-8') as f:
    f.write(res.stdout)
print("Done, length:", len(res.stdout))
