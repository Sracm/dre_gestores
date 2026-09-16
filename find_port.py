import subprocess

out = subprocess.check_output("netstat -ano", shell=True).decode("utf-8", errors="ignore")
lines = [l for l in out.splitlines() if "LISTENING" in l]

# find msmdsrv PID
out2 = subprocess.check_output("tasklist /FI \"IMAGENAME eq msmdsrv.exe\"", shell=True).decode("utf-8", errors="ignore")
print("TASKLIST:")
print(out2)

pids = []
for l in out2.splitlines():
    if "msmdsrv.exe" in l:
        parts = l.split()
        if len(parts) >= 2:
            pids.append(parts[1])

print(f"PIDs found: {pids}")

ports = []
for l in lines:
    for pid in pids:
        if l.strip().endswith(pid):
            ports.append(l)

print("PORTS:")
for p in ports:
    print(p)
