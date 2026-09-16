import subprocess

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT MEASURE_NAME, MEASURE_CAPTION, EXPRESSION FROM `$SYSTEM.MDSCHEMA_MEASURES"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

foreach ($row in $dt.Rows) {
    $n = [string]$row["MEASURE_NAME"]
    if ($n -like "*antonio*" -or $n -like "*TESTE*" -or $n -eq ".." -or $n -like "*REALIZADO*" -or $n -like "*ORÇADO*") {
        Write-Host "NAME:" $row["MEASURE_NAME"] "CAPTION:" $row["MEASURE_CAPTION"]
        Write-Host "EXPR:" $row["EXPRESSION"]
        Write-Host "--------------------"
    }
}
$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print(res.stdout)
with open('scratch/md_measures_out.txt', 'w', encoding='utf-8') as f:
    f.write(res.stdout)
