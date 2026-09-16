import psutil

for conn in psutil.net_connections(kind='tcp'):
    if conn.status == 'LISTEN':
        try:
            proc = psutil.Process(conn.pid)
            if proc.name().lower() == 'msmdsrv.exe':
                print(f"Port: {conn.laddr.port}, PID: {conn.pid}")
        except:
            pass
