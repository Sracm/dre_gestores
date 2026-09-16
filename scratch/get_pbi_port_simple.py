import subprocess
import re

out = subprocess.check_output('tasklist /fi "imagename eq msmdsrv.exe" /nh', shell=True, text=True)
pids = []
for line in out.strip().split('\n'):
    parts = line.split()
    if len(parts) >= 2 and parts[1].isdigit():
        pids.append(parts[1])

if not pids:
    print("No msmdsrv running.")
    exit(0)

netstat = subprocess.check_output('netstat -ano', shell=True, text=True)
for line in netstat.strip().split('\n'):
    if 'LISTENING' in line:
        parts = line.split()
        if len(parts) >= 5:
            pid = parts[-1]
            if pid in pids:
                print(f"Port: {parts[1]}")
