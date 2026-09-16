import subprocess
import sqlite3

valid_port = 60886
ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:""" + str(valid_port) + """;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZE(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS], VMQ_TSICUS[DESCRCENCUS])
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$conn.Close()

$dt | ConvertTo-Json
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
import json
try:
    data = json.loads(res.stdout)
    for r in data:
        if 'DESCRCENCUS' in str(r).upper() and 'PRODUTO' in str(r).upper():
            print(r)
except Exception as e:
    print(e)
