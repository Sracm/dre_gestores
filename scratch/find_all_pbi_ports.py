import subprocess
import re
import time

def get_pbi_ports():
    """Find all Power BI Desktop ADOMD ports"""
    result = subprocess.run(
        ['powershell', '-Command', 
         'Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -gt 49000 -and $_.LocalPort -lt 65000} | Select-Object LocalPort | Sort-Object LocalPort'],
        capture_output=True, text=True, timeout=30
    )
    
    ports = []
    for line in result.stdout.split('\n'):
        line = line.strip()
        if line.isdigit():
            ports.append(int(line))
    return ports

def test_port(port, dax_query="EVALUATE {1}"):
    """Test if a port is a PBI ADOMD port"""
    ps_script = f"""
Add-Type -Path "C:\\Program Files\\Microsoft.NET\\ADOMD.NET\\160\\Microsoft.AnalysisServices.AdomdClient.dll"
try {{
    $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:{port}")
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = '{dax_query}'
    $reader = $cmd.ExecuteReader()
    $conn.Close()
    Write-Output "OK"
}} catch {{
    Write-Output "FAIL: $($_.Exception.Message.Split([char]13)[0])"
}}
"""
    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip()

print("Procurando portas abertas...")
ports = get_pbi_ports()
print(f"Portas candidatas: {ports}")

print("\nTestando portas...")
for port in ports:
    result = test_port(port)
    print(f"  Porta {port}: {result}")
    if result == "OK":
        print(f"\n==> PORTA ATIVA: {port}")
