import subprocess

cmd = ['powershell', '-Command', 'Get-Process | Where-Object { $_.ProcessName -match "msmdsrv|PBIDesktop" } | Select-Object Id, ProcessName, MainWindowTitle']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
