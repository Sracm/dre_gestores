import subprocess

ps = r"""
[System.Reflection.Assembly]::LoadFrom('C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll') | Out-Null
foreach ($p in @(63263, 53363, 53385)) {
    try {
        $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$p;")
        $conn.Open()
        Write-Host "Port $p SUCCESS, Database: $($conn.Database)"
        $conn.Close()
    } catch {
        Write-Host "Port $p FAILED: $($_.Exception.Message)"
    }
}
"""

res = subprocess.run(['powershell', '-Command', ps], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
