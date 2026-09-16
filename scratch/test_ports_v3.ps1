$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"

# Use PowerShell's own reflection to load
$bytes = [System.IO.File]::ReadAllBytes($adomdPath)
[System.Reflection.Assembly]::Load($bytes) | Out-Null

foreach ($port in @(49676, 57430)) {
    Write-Host "Testando porta $port..."
    try {
        $connStr = "Data Source=localhost:$port"
        $conn = New-Object Microsoft.PowerBI.AdomdClient.AdomdConnection($connStr)
        $conn.Open()
        Write-Host "  => CONEXAO OK porta $port" -ForegroundColor Green
        $conn.Close()
    } catch {
        $msg = $_.Exception.Message
        if ($msg.Length -gt 150) { $msg = $msg.Substring(0, 150) }
        Write-Host "  => FALHA $port : $msg"
    }
}
