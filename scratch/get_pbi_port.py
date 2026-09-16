import subprocess

cmd = ['powershell', '-Command', 'Get-NetTCPConnection -OwningProcess 9756 | Where-Object { $_.State -eq "Listen" } | Select-Object LocalPort']
res = subprocess.run(cmd, capture_output=True, text=True)
print("msmdsrv Listen Ports:")
print(res.stdout)
