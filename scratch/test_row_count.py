import subprocess

valid_port = 60886
ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:""" + str(valid_port) + """;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 9),
    "ROWS", COUNTROWS(VMQ_TSICUS)
)
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
print("POWERSHELL OUTPUT:", res.stdout)
if res.stderr:
    print("POWERSHELL ERR:", res.stderr)
