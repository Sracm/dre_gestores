$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null
$connType = [System.Reflection.Assembly]::LoadFrom($adomdPath).GetType("Microsoft.PowerBI.AdomdClient.AdomdConnection")

foreach ($port in @(49676, 57430)) {
    Write-Host "Testando porta $port..."
    try {
        $conn = [System.Activator]::CreateInstance($connType, "Data Source=localhost:$port")
        $conn.Open()
        Write-Host "  => CONEXAO OK na porta $port" -ForegroundColor Green
        $conn.Close()
    } catch {
        $msg = $_.Exception.Message
        if ($msg.Length -gt 150) { $msg = $msg.Substring(0, 150) }
        Write-Host "  => FALHA: $msg"
    }
}
